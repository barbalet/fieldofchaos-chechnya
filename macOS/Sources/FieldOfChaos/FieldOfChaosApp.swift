import SwiftUI
import CFieldOfChaos

@main
struct FieldOfChaosApp: App {
    @StateObject private var game = GameModel()
    var body: some Scene {
        Window("Field of Chaos — Chechnya", id: "battle") {
            BattleView(game: game)
                .frame(minWidth: 1050, minHeight: 720)
        }
        .defaultSize(width: 1250, height: 820)
        .commands {
            CommandGroup(replacing: .newItem) {
                Button("New Operation") { game.newGame() }.keyboardShortcut("n")
            }
        }
    }
}

struct BattleView: View {
    @ObservedObject var game: GameModel
    @State private var showManual = false
    private let blue = Color(red: 0.53, green: 0.78, blue: 0.81)
    private let orange = Color(red: 0.91, green: 0.64, blue: 0.43)
    var body: some View {
        VStack(alignment: .leading, spacing: 18) {
            HStack {
                VStack(alignment: .leading) {
                    Text("FIELD OF CHAOS").font(.caption).tracking(3).foregroundStyle(.secondary)
                    Text("A city in the crossfire.").font(.largeTitle.bold())
                    Text("Chechnya · Gold rules · Native C engine").foregroundStyle(.secondary)
                }
                Spacer()
                Button("Field manual") { showManual = true }
                Button("New operation") { game.newGame() }
            }
            HStack {
                Toggle("Autopilot · AI plays both patrols", isOn: Binding(get: { game.automatic }, set: game.setAutopilot))
                    .toggleStyle(.switch).accessibilityIdentifier("autopilot")
                Spacer()
                Toggle("Computer opponent", isOn: Binding(get: { game.computerOpponent }, set: game.setComputerOpponent))
                    .help("Turn off for shared-device two-player play.")
            }
            HStack(alignment: .top, spacing: 20) {
                VStack(alignment: .leading, spacing: 12) {
                    HStack {
                        Text(game.title).font(.headline).accessibilityIdentifier("battle-status")
                        Spacer()
                        Text(game.busy ? (game.automatic ? "AUTOPILOT" : "COMPUTER TURN") : game.finished ? "OPERATION COMPLETE" : "YOUR TURN")
                            .font(.caption).foregroundStyle(.secondary)
                    }
                    GeometryReader { geometry in
                        let size = min(geometry.size.width / 24, geometry.size.height / 16)
                        ZStack(alignment: .topLeading) {
                        VStack(spacing: 1) {
                            ForEach(0..<16, id: \.self) { y in
                                HStack(spacing: 1) {
                                    ForEach(0..<24, id: \.self) { x in cell(x, y).frame(width: max(1, size - 1), height: max(1, size - 1)) }
                                }
                            }
                        }
                        if game.controllable && (game.action == .move || game.action == .run) {
                            Circle().stroke(blue.opacity(0.7), style: StrokeStyle(lineWidth: 1.5, dash: [5, 3]))
                                .frame(width: game.movementRadius * size * 2, height: game.movementRadius * size * 2)
                                .position(x: (Double(game.value(game.selected, 0)) + 0.5) * size,
                                          y: (Double(game.value(game.selected, 1)) + 0.5) * size)
                                .allowsHitTesting(false).accessibilityHidden(true)
                        }
                        }.clipped()
                    }
                    .aspectRatio(24.0 / 16, contentMode: .fit)
                    HStack {
                        Label("North patrol", systemImage: "circle.fill").foregroundStyle(blue)
                        Label("South patrol", systemImage: "circle.fill").foregroundStyle(orange)
                        Text("▧ Rubble: cover   ▰ Ruins: blocks sight").foregroundStyle(.secondary)
                    }.font(.caption)
                    Text(game.busy ? "Watching the battle. Disable Autopilot to take control." : game.message)
                        .font(.callout).foregroundStyle(.secondary)
                }
                VStack(alignment: .leading, spacing: 12) {
                    Text(game.name(game.selected)).font(.title3.bold())
                    Text("\(game.weapon(game.selected)) · \(game.value(game.selected, 5))/10 rounds\n\(game.value(game.selected, 6)) spare clips\n\(game.value(game.selected, 28) != 0 ? "Movement spent (focused shot)" : game.value(game.selected, 27) == 2 ? "Ran" : game.value(game.selected, 3) != 0 ? "Moved" : "Move ready") / \(game.value(game.selected, 4) != 0 ? "Action spent" : "Action ready")")
                        .font(.callout).foregroundStyle(.secondary)
                    Text("Skills").font(.caption.bold())
                    Text(game.skills(game.selected).joined(separator: " · ")).font(.caption).foregroundStyle(.secondary)
                    Text(game.value(game.selected, 7) != 0 ? "Weapon jammed — clear before firing" : game.value(game.selected, 27) == 2 ? "Running · harder to hit" : game.value(game.selected, 28) != 0 ? "Focused shot · movement spent" : "").font(.caption)
                    ForEach(0..<7, id: \.self) { location in
                        HStack { Text(GameModel.locations[location].capitalized); Spacer(); Text("\(game.value(game.selected, location + 11))") }
                            .font(.caption).monospacedDigit()
                    }
                    Picker("Action", selection: $game.action) {
                        ForEach(GameModel.Action.allCases, id: \.self) { Text($0.rawValue).tag($0) }
                    }.pickerStyle(.menu).disabled(!game.controllable)
                    .onChange(of: game.action) { _, choice in
                        switch choice {
                        case .move: game.message = "Choose a highlighted destination; the action remains available."
                        case .run: game.message = "Run expands movement and spends the action. Choose a highlighted destination."
                        case .fire: game.message = "Choose an opposing target. Normal movement remains available."
                        case .focus: game.message = "Focused shot requires no movement: +1 aiming die, +2 with Sniper Training."
                        case .aid: game.message = "Choose yourself or an adjacent standing ally for treatment."
                        }
                    }
                    Button("Reload / clear jam") { game.reloadSelected() }.disabled(!game.controllable || game.value(game.selected, 4) != 0)
                    Button("End patrol turn →") { game.endTurn() }
                        .buttonStyle(.borderedProminent).disabled(game.busy || game.finished)
                    Divider()
                    Text("FIELD REPORT").font(.caption).tracking(2)
                    ScrollView {
                        VStack(alignment: .leading, spacing: 10) {
                            ForEach(Array(game.reports.enumerated()), id: \.offset) { _, report in Text(report).font(.caption).frame(maxWidth: .infinity, alignment: .leading) }
                        }
                    }.frame(maxHeight: .infinity)
                }.frame(width: 275)
            }
        }
        .padding(24).background(Color(red: 0.07, green: 0.09, blue: 0.08))
        .preferredColorScheme(.dark)
        .sheet(isPresented: $showManual) {
            VStack(alignment: .leading, spacing: 16) {
                Text("Field manual").font(.title.bold())
                Text("Incapacitate all five opposing units. Select a friendly unit, choose Move, Fire or First aid, then click the destination or target. Each unit gets one move and one action per patrol turn. Run expands movement by 50%, or doubles it with Running, and consumes the action. Focused shot requires no movement, adds one aiming die and consumes movement; Sniper Training adds a second aiming die. Running targets impose a two-die penalty; moving targets impose a one-die penalty. These aiming and running choices are explicit skirmish adaptations. First aid targets yourself or an adjacent standing ally.")
                Text("Rubble provides light cover. Ruins block movement and sight. One cell equals two tabletop inches. Movement uses true straight-line distance within the dashed circle. Highlighted destinations are legal; ruins and standing units block the route, including diagonal corner crossings. Fire consumes ammunition; reload consumes an action and a spare clip. Losing an arm prevents shooting; depletion of head, chest or abdomen incapacitates a unit.")
                Text("Autopilot controls both patrols, one unit every 0.7 seconds. Switch it off at any time to take control of the current patrol. Already spent moves and actions stay spent. It stops at victory. Computer opponent controls South only; disable it for shared-device two-player play.")
                Text("This fictional skirmish uses the existing Gold C rules. Grid terrain, distance, turn structure, fixed loadouts and victory are game adaptations. Grenades, shotguns, melee, character creation, campaigns and saved games are not included in this native version.").foregroundStyle(.secondary)
                Button("Return to operation") { showManual = false }.keyboardShortcut(.defaultAction)
            }.padding(30).frame(width: 600)
        }
    }
    private func cell(_ x: Int, _ y: Int) -> some View {
        let unit = game.occupant(x, y)
        let ground = terrain(Int32(x), Int32(y))
        return Button { game.click(x, y) } label: {
            ZStack {
                Rectangle().fill(ground == 2 ? Color.gray.opacity(0.6) : ground == 1 ? Color.brown.opacity(0.5) : Color.white.opacity(0.045))
                if ground != 0 { Text(ground == 2 ? "▰" : "▧").foregroundStyle(.secondary).font(.caption) }
                if let unit {
                    Circle().fill(unit < game.patrolSize ? blue : orange).padding(2)
                    Text("\(unit % game.patrolSize + 1)").font(.system(size: 12, weight: .bold)).foregroundStyle(.black)
                }
                Rectangle().strokeBorder(unit == game.selected ? Color.yellow : game.reachable(x, y) ? blue : unit.map(game.targetable) == true ? orange : Color.clear, lineWidth: 2)
            }.contentShape(Rectangle())
        }
        .buttonStyle(.plain)
        .accessibilityLabel("Column \(x + 1), row \(y + 1), \(unit.map(game.name) ?? (ground == 2 ? "ruins" : ground == 1 ? "rubble" : "street"))")
    }
}
