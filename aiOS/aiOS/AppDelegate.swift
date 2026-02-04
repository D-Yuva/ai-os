import AppKit
import SwiftUI

class AppDelegate: NSObject, NSApplicationDelegate {

    private var window: NSWindow!

    func applicationDidFinishLaunching(_ notification: Notification) {
        createWindow()
        registerHotKey()
    }

    // MARK: - Window creation (Spotlight-style)

    private func createWindow() {
        let contentView = ContentView()

        window = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 560, height: 90),
            styleMask: [
                .titled,
                .fullSizeContentView
            ],
            backing: .buffered,
            defer: false
        )

        window.center()
        window.level = .floating
        window.isReleasedWhenClosed = false

        // 🔥 Liquid glass requirements
        window.isOpaque = false
        window.backgroundColor = .clear
        window.titleVisibility = .hidden
        window.titlebarAppearsTransparent = true

        // ❌ REMOVE DUPLICATE BUTTONS
        window.standardWindowButton(.miniaturizeButton)?.isHidden = true
        window.standardWindowButton(.zoomButton)?.isHidden = true

        // Optional: keep close only
        window.standardWindowButton(.closeButton)?.isHidden = false

        window.contentView = NSHostingView(rootView: contentView)

        window.orderOut(nil) // start hidden
    }

    // MARK: - Global Hotkey (⌘⌥M)

    private func registerHotKey() {
        NSEvent.addGlobalMonitorForEvents(matching: .keyDown) { [weak self] event in
            guard let self else { return }

            if event.modifierFlags.contains([.command, .option]),
               event.keyCode == 46 { // M
                self.toggleWindow()
            }
        }
    }

    // MARK: - Toggle visibility

    private func toggleWindow() {
        if window.isVisible {
            window.orderOut(nil)
        } else {
            window.center()
            window.makeKeyAndOrderFront(nil)
            NSApp.activate(ignoringOtherApps: true)
        }
    }
}
