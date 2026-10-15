import SwiftUI
import CFieldOfChaos

@MainActor
final class GameModel: ObservableObject {
    enum Action: String, CaseIterable { case move = "Move", fire = "Fire", aid = "First aid" }
    @Published var selected = 0
    @Published var action: Action = .move
    @Published var reports: [String] = []
    @Published var revision = 0
    @Published private(set) var automatic = false
    @Published private(set) var busy = false
    @Published private(set) var computerOpponent = true
    @Published var message = "Select a unit, choose an action, then click a cell or target."
    private var task: Task<Void, Never>?
    private var generation = 0
    private var nextUnit = 0
    let interval: Duration
    static let locations = ["left leg", "right leg", "chest", "abdomen", "left arm", "right arm", "head"]

    init(seed: UInt32 = .random(in: .min ... .max), interval: Duration = .milliseconds(700)) {
        self.interval = interval
        newGame(seed: seed)
    }
    func value(_ unit: Int = 0, _ key: Int) -> Int { Int(state(Int32(unit), Int32(key))) }
    var side: Int { value(0, 20) }
    var round: Int { value(0, 21) }
    var winner: Int { value(0, 22) }
    var title: String { winner >= 0 ? "\(winner == 0 ? "North" : "South") patrol wins" : "Round \(round) · \(side == 0 ? "North" : "South") patrol" }
    func name(_ i: Int) -> String { "\(i < 3 ? "North" : "South") \(i % 3 + 1) · \(i % 3 == 0 ? "Rifleman" : i % 3 == 1 ? "Scout" : "Medic")" }
    func standing(_ i: Int) -> Bool { value(i, 2) != 0 }
    var controllable: Bool { !busy && winner < 0 && standing(selected) && selected / 3 == side }
    func occupant(_ x: Int, _ y: Int) -> Int? { (0..<6).first { standing($0) && value($0, 0) == x && value($0, 1) == y } }
    func reachable(_ x: Int, _ y: Int) -> Bool { controllable && action == .move && can_move(Int32(selected), Int32(x), Int32(y)) != 0 }
    func targetable(_ i: Int) -> Bool { controllable && action == .fire && can_attack(Int32(selected), Int32(i)) != 0 }
    func record(_ text: String) { reports.insert(text, at: 0); if reports.count > 150 { reports.removeLast() } }
    func refresh() { revision += 1 }

    private func cancel() {
        generation += 1
        task?.cancel(); task = nil; busy = false
    }
    func newGame(seed: UInt32 = .random(in: .min ... .max)) {
        cancel(); CFieldOfChaos.start(seed); selected = 0; action = .move; nextUnit = 0
        reports = ["Operation started. Incapacitate the opposing patrol."]
        refresh(); schedule()
    }
    func setAutopilot(_ enabled: Bool) {
        cancel(); automatic = enabled && winner < 0
        selected = (side * 3 ..< side * 3 + 3).first(where: standing) ?? 0
        nextUnit = side * 3
        record(automatic ? "Autopilot enabled: AI plays both patrols." : "Autopilot disabled: you control the current patrol.")
        refresh()
        if automatic { schedule() }
    }
    func setComputerOpponent(_ enabled: Bool) {
        computerOpponent = enabled
        cancel(); nextUnit = side * 3; schedule()
    }
    func click(_ x: Int, _ y: Int) {
        guard !busy, winner < 0 else { return }
        let target = occupant(x, y)
        if controllable, action == .aid, let target, target / 3 == side {
            if heal(Int32(selected), Int32(target)) != 0 { healingReport(); refresh(); return }
        }
        if let target, target / 3 == side { selected = target; return }
        guard controllable else { return }
        if action == .move, move_unit(Int32(selected), Int32(x), Int32(y)) != 0 {
            record("\(name(selected)) moved to \(x + 1), \(y + 1).")
        } else if action == .fire, let target, attack(Int32(selected), Int32(target)) != 0 {
            attackReport(selected, target)
        } else { message = "Unavailable action. Choose a highlighted cell or valid target." }
        refresh()
    }
    func reloadSelected() {
        guard controllable else { return }
        if CFieldOfChaos.reload(Int32(selected)) != 0 { record("\(name(selected)) reloaded / cleared jam.") }
        else { message = "Action spent, magazine full, or no spare clips." }
        refresh()
    }
    func endTurn() {
        guard !busy, winner < 0 else { return }
        _ = end_turn(); nextUnit = side * 3; selected = nextUnit
        record("Patrol turn ended."); refresh(); schedule()
    }
    private func attackReport(_ i: Int, _ j: Int) {
        let location = Self.locations[value(0, 25)]
        record("\(name(i)) → \(name(j)): \(value(0, 23)) vs \(value(0, 24)). \(value(0, 26) != 0 ? "Hit: \(location)." : "Miss.")\(!standing(j) ? " Incapacitated." : "")")
    }
    private func healingReport() { record("\(name(selected)): first aid \(value(0, 26) != 0 ? "restored a wound" : "failed").") }

    private func schedule() {
        guard winner < 0, automatic || (computerOpponent && side == 1) else { return }
        busy = true
        let run = generation
        task = Task { [weak self] in
            while let self, !Task.isCancelled, run == self.generation {
                do { try await Task.sleep(for: self.interval) } catch { return }
                guard !Task.isCancelled, run == self.generation else { return }
                self.stepAI()
                if self.winner >= 0 {
                    self.automatic = false; self.busy = false
                    self.record("Operation complete. Autopilot stopped."); self.refresh(); return
                }
                if !self.automatic && !(self.computerOpponent && self.side == 1) {
                    self.busy = false; self.selected = self.side * 3; self.refresh(); return
                }
            }
        }
    }
    // One unit per tick. All legality, dice and wound changes remain in C.
    func stepAI() {
        guard winner < 0 else { return }
        let first = side * 3
        if nextUnit < first || nextUnit >= first + 3 { nextUnit = first }
        let i = nextUnit; selected = i
        if standing(i) {
            let enemies = (0..<6).filter { $0 / 3 != side && standing($0) }.sorted {
                distance(i, $0) < distance(i, $1)
            }
            if value(i, 4) == 0 && (value(i, 7) != 0 || value(i, 5) < 2) {
                if CFieldOfChaos.reload(Int32(i)) != 0 { record("\(name(i)) serviced its weapon.") }
            }
            if let target = enemies.first, !enemies.contains(where: { can_attack(Int32(i), Int32($0)) != 0 }) {
                let distances = approach(target)
                let choices = (0..<384).filter { can_move(Int32(i), Int32($0 % 24), Int32($0 / 24)) != 0 }
                if let cell = choices.min(by: { distances[$0] < distances[$1] }), distances[cell] < 1000 {
                    _ = move_unit(Int32(i), Int32(cell % 24), Int32(cell / 24))
                    record("\(name(i)) advanced.")
                }
            }
            if let target = enemies.first(where: { can_attack(Int32(i), Int32($0)) != 0 }) {
                if attack(Int32(i), Int32(target)) != 0 { attackReport(i, target) }
            } else if heal(Int32(i), Int32(i)) != 0 { healingReport() }
        }
        nextUnit += 1
        if nextUnit == first + 3, winner < 0 { _ = end_turn(); nextUnit = side * 3; record("Patrol turn ended.") }
        refresh()
    }
    private func distance(_ a: Int, _ b: Int) -> Int { max(abs(value(a, 0) - value(b, 0)), abs(value(a, 1) - value(b, 1))) }
    private func approach(_ target: Int) -> [Int] {
        var distances = Array(repeating: 1000, count: 384)
        var queue = [value(target, 1) * 24 + value(target, 0)]
        distances[queue[0]] = 0
        var head = 0
        while head < queue.count {
            let cell = queue[head]; head += 1
            for (dx, dy) in [(1,0),(-1,0),(0,1),(0,-1)] {
                let x = cell % 24 + dx, y = cell / 24 + dy
                guard terrain(Int32(x), Int32(y)) != 2 else { continue }
                let next = y * 24 + x
                if distances[next] == 1000 { distances[next] = distances[cell] + 1; queue.append(next) }
            }
        }
        return distances
    }
}
