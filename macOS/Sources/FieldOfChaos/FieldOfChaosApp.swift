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
                        VStack(spacing: 1) {
                            ForEach(0..<16, id: \.self) { y in
                                HStack(spacing: 1) {
                                    ForEach(0..<24, id: \.self) { x in cell(x, y).frame(width: max(1, size - 1), height: max(1, size - 1)) }
                                }
                            }
                        }
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
                    Text("\(game.value(game.selected, 9) == 1 ? "Rifle" : "Carbine") · \(game.value(game.selected, 5))/10 rounds\n\(game.value(game.selected, 6)) spare clips\n\(game.value(game.selected, 3) != 0 ? "Moved" : "Move ready") / \(game.value(game.selected, 4) != 0 ? "Action spent" : "Action ready")")
                        .font(.callout).foregroundStyle(.secondary)
                    ForEach(0..<7, id: \.self) { location in
                        HStack { Text(GameModel.locations[location].capitalized); Spacer(); Text("\(game.value(game.selected, location + 11))") }
                            .font(.caption).monospacedDigit()
                    }
                    Picker("Action", selection: $game.action) {
                        ForEach(GameModel.Action.allCases, id: \.self) { Text($0.rawValue).tag($0) }
                    }.pickerStyle(.segmented).disabled(!game.controllable)
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
                Text("Incapacitate all three opposing units. Select a friendly unit, choose Move, Fire or First aid, then click the destination or target. Each unit gets one move and one action per patrol turn. First aid targets yourself or an adjacent standing ally.")
                Text("Rubble provides light cover. Ruins block movement and sight. One cell equals two tabletop inches. Fire consumes ammunition; reload consumes an action and a spare clip. Losing an arm prevents shooting; depletion of head, chest or abdomen incapacitates a unit.")
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
                    Circle().fill(unit < 3 ? blue : orange).padding(2)
                    Text("\(unit % 3 + 1)").font(.system(size: 12, weight: .bold)).foregroundStyle(.black)
                }
                Rectangle().strokeBorder(unit == game.selected ? Color.yellow : game.reachable(x, y) ? blue : unit.map(game.targetable) == true ? orange : Color.clear, lineWidth: 2)
            }.contentShape(Rectangle())
        }
        .buttonStyle(.plain)
        .accessibilityLabel("Column \(x + 1), row \(y + 1), \(unit.map(game.name) ?? (ground == 2 ? "ruins" : ground == 1 ? "rubble" : "street"))")
    }
}
