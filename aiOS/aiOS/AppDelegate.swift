import AppKit
import SwiftUI

class AppDelegate: NSObject, NSApplicationDelegate {

    var window: NSWindow!

    // MARK: - App lifecycle

    func applicationDidFinishLaunching(_ notification: Notification) {
        setupWindow()
        registerHotKey()
    }

    // MARK: - Window setup

    private func setupWindow() {
        let contentView = ContentView()

        window = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 600, height: 80),
            styleMask: [.titled, .fullSizeContentView],
            backing: .buffered,
            defer: false
        )

        window.center()
        window.isReleasedWhenClosed = false
        window.level = .floating
        window.titleVisibility = .hidden
        window.titlebarAppearsTransparent = true
        window.isOpaque = false
        window.backgroundColor = .clear
        window.contentView = NSHostingView(rootView: contentView)

        window.orderOut(nil) // start hidden
    }

    // MARK: - Global hotkey

    private func registerHotKey() {
        NSEvent.addGlobalMonitorForEvents(matching: .keyDown) { [weak self] event in
            guard let self = self else { return }

            if event.modifierFlags.contains([.command, .option]),
               event.keyCode == 46 { // M key
                self.toggleWindow()
            }
        }
    }

    // MARK: - Window toggle

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
