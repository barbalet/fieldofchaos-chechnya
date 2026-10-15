import XCTest
import CFieldOfChaos
@testable import FieldOfChaos

final class GameModelTests: XCTestCase {
    @MainActor func testManualMovementAndTurnOwnership() {
        let game = GameModel(seed: 123)
        game.setComputerOpponent(false)
        game.click(3, 3)
        XCTAssertEqual(game.value(0, 0), 3)
        game.click(4, 3)
        XCTAssertEqual(game.value(0, 0), 3, "A unit cannot move twice")
        game.endTurn()
        XCTAssertEqual(game.side, 1)
        XCTAssertEqual(can_move(0, 4, 3), 0)
    }
    @MainActor func testAIAdvancesBothPatrols() {
        let game = GameModel(seed: 123)
        game.setComputerOpponent(false)
        for _ in 0..<6 { game.stepAI() }
        XCTAssertEqual(game.round, 2)
        XCTAssertTrue(game.reports.contains { $0.hasPrefix("North") && $0.contains("advanced") })
        XCTAssertTrue(game.reports.contains { $0.hasPrefix("South") && $0.contains("advanced") })
    }
    @MainActor func testAutopilotCancellationAndReset() async throws {
        let game = GameModel(seed: 123, interval: .milliseconds(2))
        game.setComputerOpponent(false)
        game.setAutopilot(true)
        for _ in 0..<100 {
            if game.round > 1 { break }
            try await Task.sleep(for: .milliseconds(5))
        }
        XCTAssertGreaterThan(game.round, 1)
        game.setAutopilot(false)
        let snapshot = (0..<6).flatMap { i in (0...17).map { game.value(i, $0) } }
        let round = game.round, side = game.side
        try await Task.sleep(for: .milliseconds(15))
        XCTAssertEqual(snapshot, (0..<6).flatMap { i in (0...17).map { game.value(i, $0) } })
        XCTAssertEqual(game.round, round); XCTAssertEqual(game.side, side)
        XCTAssertFalse(game.busy)
        game.setAutopilot(true); game.newGame(seed: 456); game.setAutopilot(false)
        try await Task.sleep(for: .milliseconds(15))
        XCTAssertEqual(game.round, 1); XCTAssertEqual(game.side, 0)
        XCTAssertEqual(game.value(0, 0), 2)
    }
    @MainActor func testAutopilotStopsWhenBothPatrolsExhaustAmmunition() async throws {
        // Seed 279 previously ran forever with one fully healed, empty unit
        // on each side. Exercise the real engine and scheduled AI, not a mock.
        let game = GameModel(seed: 279, interval: .milliseconds(1))
        game.setAutopilot(true)
        let deadline = ContinuousClock.now + .seconds(5)
        while game.automatic && ContinuousClock.now < deadline {
            try await Task.sleep(for: .milliseconds(5))
        }
        defer { game.setAutopilot(false) }
        XCTAssertTrue(game.isDraw)
        XCTAssertLessThan(game.winner, 0, "Ammunition exhaustion must not award a victory")
        for side in 0...1 {
            let survivors = (side * 3 ..< side * 3 + 3).filter(game.standing)
            XCTAssertFalse(survivors.isEmpty)
            for unit in survivors {
                XCTAssertLessThan(game.value(unit, 5), 2)
                XCTAssertEqual(game.value(unit, 6), 0)
            }
        }
        XCTAssertFalse(game.automatic)
        XCTAssertFalse(game.busy)
        XCTAssertFalse(game.controllable)
        XCTAssertTrue(game.title.contains("Draw"))
        XCTAssertTrue(game.reports.contains { $0.contains("both patrols are out of ammunition") })
        let snapshot = (0..<6).flatMap { i in (0...17).map { game.value(i, $0) } }
        let round = game.round, side = game.side
        game.setAutopilot(true) // A terminal battle cannot restart its timer.
        game.endTurn()
        try await Task.sleep(for: .milliseconds(15))
        XCTAssertFalse(game.automatic)
        XCTAssertEqual(game.round, round); XCTAssertEqual(game.side, side)
        XCTAssertEqual(snapshot, (0..<6).flatMap { i in (0...17).map { game.value(i, $0) } })
        game.newGame(seed: 123)
        XCTAssertFalse(game.isDraw)
        XCTAssertFalse(game.finished)
        XCTAssertTrue(game.controllable)
    }

    @MainActor func testOneEmptyPatrolDoesNotEndBattleWhileOtherCanFire() {
        let game = GameModel(seed: 279)
        game.setComputerOpponent(false)
        var observedOneEmptyPatrol = false
        for _ in 0..<600 {
            let empty = (0...1).map { side in
                !(side * 3 ..< side * 3 + 3).contains {
                    game.standing($0) && (game.value($0, 5) >= 2 || game.value($0, 6) > 0)
                }
            }
            if empty[0] != empty[1], game.winner < 0 {
                observedOneEmptyPatrol = true
                XCTAssertFalse(game.isDraw)
                XCTAssertFalse(game.finished)
            }
            if game.finished { break }
            game.stepAI()
        }
        XCTAssertTrue(observedOneEmptyPatrol)
        XCTAssertTrue(game.isDraw)
    }

}
