import XCTest
import CFieldOfChaos
@testable import FieldOfChaos

final class GameModelTests: XCTestCase {
    // Save format v2 fixtures: C character followed by seven int fields.
    // Assertions against state() catch accidental fixture layout drift.
    @MainActor private func setAmmo(_ i: Int, _ rounds: Int32, _ clips: Int32 = 0) {
        let stride = Int(save_size()) / Int(unit_count())
        let pointer = UnsafeMutableRawPointer(bitPattern: UInt(save_ptr()))!
        pointer.storeBytes(of: clips, toByteOffset: i * stride + stride - 40, as: Int32.self)
        pointer.storeBytes(of: rounds, toByteOffset: i * stride + stride - 36, as: Int32.self)
        XCTAssertEqual(state(Int32(i), 5), rounds)
        XCTAssertEqual(state(Int32(i), 6), clips)
    }
    @MainActor private func position(_ i: Int, _ x: Int32, _ y: Int32) {
        let stride = Int(save_size()) / Int(unit_count())
        let pointer = UnsafeMutableRawPointer(bitPattern: UInt(save_ptr()))!
        pointer.storeBytes(of: x, toByteOffset: i * stride + stride - 28, as: Int32.self)
        pointer.storeBytes(of: y, toByteOffset: i * stride + stride - 24, as: Int32.self)
        XCTAssertEqual(state(Int32(i), 0), x)
    }
    @MainActor func testFivePersonPatrolsAndSkills() {
        let game = GameModel(seed: 123)
        XCTAssertEqual(game.unitCount, 10); XCTAssertEqual(game.patrolSize, 5)
        for side in 0..<2 {
            let base = side * 5
            XCTAssertEqual(game.value(base + 3, 9), 4)
            XCTAssertEqual(game.value(base + 4, 9), 0)
            XCTAssertTrue(game.skills(base + 4).contains("Sniper Training"))
            XCTAssertTrue(game.skills(base + 1).contains("Running"))
            XCTAssertTrue(game.skills(base + 2).contains("Paramedic"))
            XCTAssertFalse(game.skills(base).contains("Paramedic"))
        }
    }
    @MainActor func testCircularMovementAndRunningConsumesAction() {
        let game = GameModel(seed: 123); game.setComputerOpponent(false)
        for i in 0..<10 { XCTAssertGreaterThan(movement_range_inches(Int32(i)), 6) }
        XCTAssertEqual(game.movementRadius, 4)
        XCTAssertTrue(game.reachable(5, 3)); XCTAssertFalse(game.reachable(6, 2))
        game.selected = 1
        game.action = .move; XCTAssertFalse(game.reachable(6, 0))
        game.action = .run; XCTAssertEqual(game.movementRadius, 10)
        XCTAssertTrue(game.reachable(6, 0)); game.click(6, 0)
        XCTAssertEqual(game.value(1, 27), 2)
        XCTAssertEqual(game.value(1, 3), 1); XCTAssertEqual(game.value(1, 4), 1)
        XCTAssertEqual(can_attack(1, 5), 0); XCTAssertEqual(CFieldOfChaos.reload(1), 0)
        game.endTurn(); XCTAssertEqual(game.value(1, 27), 2, "Running remains a penalty during the enemy turn")
        game.endTurn(); XCTAssertEqual(game.value(1, 27), 0)
    }
    @MainActor func testFocusedShotLocksMovementAndSniperSkillAddsBonus() {
        let game = GameModel(seed: 123); game.setComputerOpponent(false)
        position(4, 3, 13); position(9, 8, 13)
        XCTAssertEqual(can_attack(4, 9), 0, "Sniper cannot fire under 12 inches")
        position(9, 9, 13)
        XCTAssertEqual(can_focus_attack(4, 9), 1)
        game.selected = 4; game.action = .focus; game.click(9, 13)
        XCTAssertEqual(game.value(0, 31), 2)
        XCTAssertEqual(game.value(4, 5), 9)
        XCTAssertEqual(game.value(4, 3), 1); XCTAssertEqual(game.value(4, 4), 1)
        XCTAssertEqual(move_unit(4, 4, 13), 0)
        game.newGame(seed: 123); position(5, 6, 1)
        XCTAssertEqual(focused_attack(0, 5), 1); XCTAssertEqual(game.value(0, 31), 1)
        game.newGame(seed: 123); position(5, 6, 1)
        XCTAssertEqual(move_unit(0, 3, 1), 1)
        XCTAssertEqual(can_focus_attack(0, 5), 0)
        XCTAssertEqual(can_attack(0, 5), 1, "Normal fire remains available after moving")
    }
    @MainActor func testWeaponSpecificAmmoAndDraw() {
        let game = GameModel(seed: 123)
        setAmmo(3, 2); position(3, 3, 10); position(8, 6, 10)
        XCTAssertEqual(can_attack(3, 8), 0)
        setAmmo(3, 3); XCTAssertEqual(attack(3, 8), 1)
        XCTAssertEqual(game.value(3, 5), 0)
        game.newGame(seed: 123)
        for i in 0..<10 { setAmmo(i, 0) }
        setAmmo(9, 1)
        XCTAssertFalse(game.isDraw, "A sniper with one round can still fight")
        setAmmo(9, 0); setAmmo(3, 2)
        XCTAssertTrue(game.isDraw, "Two rounds cannot fire the SMG's three-round attack")
    }
    @MainActor func testAutopilotStopsAtExhaustionAndResets() async throws {
        let game = GameModel(seed: 123, interval: .milliseconds(1))
        for i in 0..<10 { setAmmo(i, 0) }
        setAmmo(0, 2); position(5, 6, 1)
        game.setAutopilot(true)
        let deadline = ContinuousClock.now + .seconds(3)
        while game.automatic && ContinuousClock.now < deadline { try await Task.sleep(for: .milliseconds(5)) }
        defer { game.setAutopilot(false) }
        XCTAssertTrue(game.isDraw); XCTAssertFalse(game.automatic); XCTAssertFalse(game.busy)
        let round = game.round
        game.setAutopilot(true); game.endTurn()
        try await Task.sleep(for: .milliseconds(10)); XCTAssertEqual(game.round, round)
        game.newGame(seed: 123); XCTAssertFalse(game.finished); XCTAssertTrue(game.controllable)
    }
    @MainActor func testBothSidesAIAndCancellation() async throws {
        let game = GameModel(seed: 123, interval: .milliseconds(1))
        game.setComputerOpponent(false); game.setAutopilot(true)
        let deadline = ContinuousClock.now + .seconds(3)
        while game.round < 2 && ContinuousClock.now < deadline { try await Task.sleep(for: .milliseconds(5)) }
        XCTAssertGreaterThanOrEqual(game.round, 2)
        XCTAssertTrue(game.reports.contains { $0.hasPrefix("North") })
        XCTAssertTrue(game.reports.contains { $0.hasPrefix("South") })
        game.setAutopilot(false)
        let snapshot = (0..<10).flatMap { i in (0...17).map { game.value(i, $0) } }
        try await Task.sleep(for: .milliseconds(10))
        XCTAssertEqual(snapshot, (0..<10).flatMap { i in (0...17).map { game.value(i, $0) } })
        game.setAutopilot(true); game.newGame(seed: 456); game.setAutopilot(false)
        try await Task.sleep(for: .milliseconds(10))
        XCTAssertEqual(game.round, 1); XCTAssertEqual(game.value(0, 0), 2)
    }
}
