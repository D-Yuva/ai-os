import Foundation

final class BackendLauncher {

    static let shared = BackendLauncher()
    private var process: Process?

    // MARK: - Public API

    func startBackendIfNeeded() {
        // Do not start again if already running
        if let process = process, process.isRunning {
            return
        }

        guard let resourceURL = Bundle.main.resourceURL else {
            print("❌ Cannot locate app resources")
            return
        }

        let backendPath = resourceURL.appendingPathComponent("backend")
        let serverScript = backendPath.appendingPathComponent("agent_server.py")

        // ---------- DEBUG (remove later if you want) ----------
        print("📦 App resources:", resourceURL.path)
        print("🐍 Backend path:", backendPath.path)
        print("📜 Server script:", serverScript.path)
        // -----------------------------------------------------

        // Safety check: backend must exist
        let fm = FileManager.default
        guard fm.fileExists(atPath: serverScript.path) else {
            print("❌ agent_server.py not found at:", serverScript.path)
            return
        }

        let process = Process()

        // Use env to resolve python3 dynamically
        process.executableURL = URL(fileURLWithPath: "/usr/bin/env")
        process.arguments = [
            "python3",
            serverScript.path
        ]

        // Set working directory to backend folder
        process.currentDirectoryURL = backendPath

        // Capture logs (optional but useful)
        process.standardOutput = Pipe()
        process.standardError = Pipe()

        do {
            try process.run()
            self.process = process
            print("✅ Python backend started successfully")
        } catch {
            print("❌ Failed to start Python backend:", error)
        }
    }

    // MARK: - Optional: Stop backend cleanly

    func stopBackend() {
        guard let process = process, process.isRunning else { return }
        process.terminate()
        self.process = nil
        print("🛑 Python backend stopped")
    }
}
