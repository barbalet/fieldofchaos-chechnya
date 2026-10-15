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
}
