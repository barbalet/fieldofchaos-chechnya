import SwiftUI
import CFieldOfChaos

@MainActor
final class GameModel: ObservableObject {
    enum Action: String, CaseIterable { case move = "Move", run = "Run", fire = "Fire", focus = "Focused shot", aid = "First aid" }
    @Published var selected = 0
    @Published var action: Action = .move
    @Published var reports: [String] = []
    @Published var revision = 0
    @Published private(set) var automatic = false
    @Published private(set) var busy = false
    @Published private(set) var computerOpponent = true
    @Published var message = "Select a unit, choose an action, then click a cell or target."
    private var task: Task<Void, Never>?
    private var reportedFinish = false
    private var generation = 0
    private var nextUnit = 0
    let interval: Duration
    static let locations = ["left leg", "right leg", "chest", "abdomen", "left arm", "right arm", "head"]

    init(seed: UInt32 = .random(in: .min ... .max), interval: Duration = .milliseconds(700)) {
        self.interval = interval
        newGame(seed: seed)
    }
    func value(_ unit: Int = 0, _ key: Int) -> Int { Int(state(Int32(unit), Int32(key))) }
    var unitCount: Int { Int(unit_count()) }
    var patrolSize: Int { Int(patrol_size()) }
    let roleNames = ["Rifleman", "Scout", "Medic", "SMG gunner", "Sniper"]
    let weaponNames = ["Sniper rifle", "Rifle", "Carbine", "Automatic", "SMG", "Shotgun"]
    let skillNames = ["Firearm Basic", "Firearm Advanced", "Close Combat", "Improvised Weapons", "Clandestine Weapons", "Carpentry", "Weapon Manufacture", "Chemistry Basic", "Explosive Engineering", "Biology", "Chemistry Advanced", "Pharmaceutical Chemistry", "First Aid", "Paramedic", "Evade", "Marching", "Running", "Sniper Training"]
    func skills(_ i: Int) -> [String] { (0..<18).filter { unit_skill(Int32(i), Int32($0)) != 0 }.map { skillNames[$0] } }
    func weapon(_ i: Int) -> String { weaponNames[value(i, 9)] }
    var side: Int { value(0, 20) }
    var round: Int { value(0, 21) }
    var winner: Int { value(0, 22) }
    var isDraw: Bool { ammunition_exhausted() != 0 }
    var finished: Bool { winner >= 0 || isDraw }
    var title: String { isDraw ? "Draw · ammunition exhausted" : winner >= 0 ? "\(winner == 0 ? "North" : "South") patrol wins" : "Round \(round) · \(side == 0 ? "North" : "South") patrol" }
    func name(_ i: Int) -> String { "\(i < patrolSize ? "North" : "South") \(i % patrolSize + 1) · \(roleNames[i % patrolSize])" }
    func standing(_ i: Int) -> Bool { value(i, 2) != 0 }
    var controllable: Bool { !busy && !finished && standing(selected) && selected / patrolSize == side }
    func occupant(_ x: Int, _ y: Int) -> Int? { (0..<unitCount).first { standing($0) && value($0, 0) == x && value($0, 1) == y } }
    var movementRadius: Double { Double(action == .run ? run_range_inches(Int32(selected)) : movement_range_inches(Int32(selected))) / 2 }
    func reachable(_ x: Int, _ y: Int) -> Bool { controllable && ((action == .move && can_move(Int32(selected), Int32(x), Int32(y)) != 0) || (action == .run && can_run(Int32(selected), Int32(x), Int32(y)) != 0)) }
    func targetable(_ i: Int) -> Bool { controllable && ((action == .fire && can_attack(Int32(selected), Int32(i)) != 0) || (action == .focus && can_focus_attack(Int32(selected), Int32(i)) != 0)) }
    func record(_ text: String) { reports.insert(text, at: 0); if reports.count > 150 { reports.removeLast() } }
    func refresh() {
        if finished {
            cancel(); automatic = false
            if !reportedFinish {
                reportedFinish = true
                message = isDraw ? "Draw: both patrols are out of ammunition. Operation complete." : "Operation complete. Autopilot stopped."
                record(message)
            }
        }
        revision += 1
    }

    private func cancel() {
        generation += 1
        task?.cancel(); task = nil; busy = false
    }
    func newGame(seed: UInt32 = .random(in: .min ... .max)) {
        cancel(); CFieldOfChaos.start(seed); selected = 0; action = .move; nextUnit = 0
        reportedFinish = false
        message = "Select a unit, choose an action, then click a cell or target."
        reports = ["Operation started. Incapacitate the opposing patrol."]
        refresh(); schedule()
    }
    func setAutopilot(_ enabled: Bool) {
        cancel(); automatic = enabled && !finished
        selected = (side * patrolSize ..< side * patrolSize + patrolSize).first(where: standing) ?? 0
        nextUnit = side * patrolSize
        record(automatic ? "Autopilot enabled: AI plays both patrols." : "Autopilot disabled: you control the current patrol.")
        refresh()
        if automatic { schedule() }
    }
    func setComputerOpponent(_ enabled: Bool) {
        computerOpponent = enabled
        cancel(); nextUnit = side * patrolSize; schedule()
    }
    func click(_ x: Int, _ y: Int) {
        guard !busy, !finished else { return }
        let target = occupant(x, y)
        if controllable, action == .aid, let target, target / patrolSize == side {
            if heal(Int32(selected), Int32(target)) != 0 { healingReport(); refresh(); return }
        }
        if let target, target / patrolSize == side { selected = target; return }
        guard controllable else { return }
        if action == .move, move_unit(Int32(selected), Int32(x), Int32(y)) != 0 {
            record("\(name(selected)) moved to \(x + 1), \(y + 1).")
        } else if action == .run, run_unit(Int32(selected), Int32(x), Int32(y)) != 0 {
            record("\(name(selected)) ran; action spent.")
        } else if action == .focus, let target, focused_attack(Int32(selected), Int32(target)) != 0 {
            attackReport(selected, target)
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
        guard !busy, !finished else { return }
        _ = end_turn(); nextUnit = side * patrolSize; selected = nextUnit
        record("Patrol turn ended."); refresh(); schedule()
    }
    private func attackReport(_ i: Int, _ j: Int) {
        let location = Self.locations[value(0, 25)]
        record("\(name(i)) → \(name(j)): \(value(0, 23)) vs \(value(0, 24)) (\(value(0, 30)) dice, +\(value(0, 31)) focus). \(value(0, 26) != 0 ? "Hit: \(location)." : "Miss.")\(!standing(j) ? " Incapacitated." : "")")
    }
    private func healingReport() { record("\(name(selected)): first aid \(value(0, 26) != 0 ? "restored a wound" : "failed").") }

    private func schedule() {
        guard !finished, automatic || (computerOpponent && side == 1) else { return }
        busy = true
        let run = generation
        task = Task { [weak self] in
            while let self, !Task.isCancelled, run == self.generation {
                do { try await Task.sleep(for: self.interval) } catch { return }
                guard !Task.isCancelled, run == self.generation else { return }
                self.stepAI()
                if self.finished { return }
                if !self.automatic && !(self.computerOpponent && self.side == 1) {
                    self.busy = false; self.selected = self.side * patrolSize; self.refresh(); return
                }
            }
        }
    }
    // One unit per tick. All legality, dice and wound changes remain in C.
    func stepAI() {
        guard !finished else { return }
        let first = side * patrolSize
        if nextUnit < first || nextUnit >= first + patrolSize { nextUnit = first }
        let i = nextUnit; selected = i
        if standing(i) {
            let enemies = (0..<unitCount).filter { $0 / patrolSize != side && standing($0) }.sorted {
                distance(i, $0) < distance(i, $1)
            }
            if value(i, 4) == 0 && (value(i, 7) != 0 || value(i, 5) < Int(rounds_required(Int32(i)))) {
                if CFieldOfChaos.reload(Int32(i)) != 0 { record("\(name(i)) serviced its weapon.") }
            }
            if let target = enemies.first, !enemies.contains(where: { can_attack(Int32(i), Int32($0)) != 0 }) {
                let distances = approach(target)
                let separation = max(abs(value(i, 0) - value(target, 0)), abs(value(i, 1) - value(target, 1)))
                let retreat = value(i, 9) == 0 && separation < 6
                let running = !retreat && value(i, 4) == 0 && value(i, 3) == 0 && distance(i, target) > 64
                let choices: [Int] = (0..<384).filter { cell in
                    let x = Int32(cell % 24), y = Int32(cell / 24), unit = Int32(i)
                    if running { return can_run(unit, x, y) != 0 }
                    return can_move(unit, x, y) != 0
                }
                func score(_ cell: Int) -> Double {
                    if retreat { let dx = cell % 24 - value(target, 0), dy = cell / 24 - value(target, 1); return -Double(dx * dx + dy * dy) }
                    return distances[cell]
                }
                if let cell = choices.min(by: { score($0) < score($1) }), score(cell) < 1000 {
                    if running { _ = run_unit(Int32(i), Int32(cell % 24), Int32(cell / 24)) }
                    else { _ = move_unit(Int32(i), Int32(cell % 24), Int32(cell / 24)) }
                    record("\(name(i)) \(running ? "ran; action spent" : retreat ? "withdrew to sniper range" : "advanced").")
                }
            }
            if let target = enemies.first(where: { can_attack(Int32(i), Int32($0)) != 0 }) {
                let result = can_focus_attack(Int32(i), Int32(target)) != 0 ? focused_attack(Int32(i), Int32(target)) : attack(Int32(i), Int32(target))
                if result != 0 { attackReport(i, target) }
            } else if heal(Int32(i), Int32(i)) != 0 { healingReport() }
        }
        nextUnit += 1
        if nextUnit == first + patrolSize, winner < 0 { _ = end_turn(); nextUnit = side * patrolSize; record("Patrol turn ended.") }
        refresh()
    }
    private func distance(_ a: Int, _ b: Int) -> Int { (value(a, 0) - value(b, 0)) * (value(a, 0) - value(b, 0)) + (value(a, 1) - value(b, 1)) * (value(a, 1) - value(b, 1)) }
    private func approach(_ target: Int) -> [Double] {
        var distances = Array(repeating: 1000.0, count: 384)
        var queue = [value(target, 1) * 24 + value(target, 0)]
        distances[queue[0]] = 0
        var head = 0
        while head < queue.count {
            let cell = queue[head]; head += 1
            for (dx, dy) in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)] {
                let x = cell % 24 + dx, y = cell / 24 + dy
                guard terrain(Int32(x), Int32(y)) != 2 else { continue }
                let next = y * 24 + x
                if dx != 0 && dy != 0 {
                    guard terrain(Int32(x), Int32(cell / 24)) != 2,
                          terrain(Int32(cell % 24), Int32(y)) != 2 else { continue }
                }
                let cost = dx != 0 && dy != 0 ? 2.0.squareRoot() : 1.0
                if distances[next] > distances[cell] + cost + 0.000001 {
                    distances[next] = distances[cell] + cost; queue.append(next)
                }
            }
        }
        return distances
    }
}
