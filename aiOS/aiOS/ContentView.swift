import SwiftUI

struct ContentView: View {
    @State private var query = ""

    var body: some View {
        VStack {
            TextField("Ask PersonalAgent…", text: $query)
                .textFieldStyle(.plain)
                .font(.system(size: 20))
                .padding()
                .onSubmit {
                    sendQuery()
                }
        }
        .background(
            RoundedRectangle(cornerRadius: 14)
                .fill(Color(NSColor.windowBackgroundColor))
                .shadow(radius: 20)
        )
        .padding()
        .frame(width: 600, height: 80)
    }

    private func sendQuery() {
        guard !query.isEmpty else { return }

        runAgent(query)
        query = ""
        NSApp.keyWindow?.orderOut(nil)
    }
}
