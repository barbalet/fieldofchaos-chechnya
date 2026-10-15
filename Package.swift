// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "FieldOfChaos",
    platforms: [.macOS(.v14)],
    products: [.executable(name: "FieldOfChaos", targets: ["FieldOfChaos"])],
    targets: [
        .target(name: "CFieldOfChaos", path: "web/engine",
                exclude: ["include", "runtime.c"],
                sources: ["game.c", "vendor/fieldofchaosgold.c"],
                publicHeadersPath: "nativeinclude",
                cSettings: [.headerSearchPath("vendor")]),
        .executableTarget(name: "FieldOfChaos", dependencies: ["CFieldOfChaos"],
                          path: "macOS/Sources/FieldOfChaos"),
        .testTarget(name: "FieldOfChaosTests", dependencies: ["FieldOfChaos", "CFieldOfChaos"],
                    path: "macOS/Tests/FieldOfChaosTests")
    ]
)
