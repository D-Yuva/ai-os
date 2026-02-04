import SwiftUI

struct ContentView: View {

    @State private var input = ""
    @State private var output = ""
    @State private var isLoading = false
    @FocusState private var focused: Bool

    var body: some View {
        GlassEffectContainer {
            VStack(spacing: 14) {

                HStack(spacing: 10) {
                    Image(systemName: "sparkles")
                        .foregroundStyle(.secondary)

                    TextField("Ask your agent…", text: $input)
                        .textFieldStyle(.plain)
                        .font(.system(size: 16, weight: .medium))
                        .focused($focused)
                        .onSubmit(runAgent)
                }
                .padding(14)
                .glassEffect(.regular.tint(.white.opacity(0.14)).interactive(true), in: .rect(cornerRadius: 16))
                .overlay(
                    RoundedRectangle(cornerRadius: 16)
                        .stroke(Color.white.opacity(0.12))
                        .shadow(color: Color.white.opacity(0.08), radius: 1, x: 0, y: 1)
                )

                if isLoading {
                    HStack(spacing: 8) {
                        ProgressView().scaleEffect(0.8)
                        Text("Thinking…")
                            .foregroundStyle(.secondary)
                    }
                }

                if !output.isEmpty {
                    VStack {
                        GeometryReader { geometry in
                            ScrollView(.vertical, showsIndicators: true) {
                                Text(output)
                                    .font(.system(size: 14))
                                    .frame(maxWidth: .infinity, alignment: .leading)
                                    .fixedSize(horizontal: false, vertical: true)
                                    .padding(.vertical, 4)
                            }
                            .frame(minHeight: 80, maxHeight: min(geometry.size.height, 400), alignment: .top)
                        }
                        .frame(minHeight: 80, maxHeight: 400)
                    }
                    .padding(12)
                    .glassEffect(.regular.tint(.white.opacity(0.14)).interactive(true), in: .rect(cornerRadius: 14))
                    .overlay(
                        RoundedRectangle(cornerRadius: 14)
                            .stroke(Color.white.opacity(0.12))
                            .shadow(color: Color.white.opacity(0.08), radius: 1, x: 0, y: 1)
                    )
                }
            }
            .padding(18)
            .glassEffect(.regular.tint(.white.opacity(0.14)).interactive(true), in: .rect(cornerRadius: 24))
            .overlay(
                RoundedRectangle(cornerRadius: 24)
                    .stroke(Color.white.opacity(0.12))
                    .shadow(color: Color.white.opacity(0.08), radius: 1, x: 0, y: 1)
            )
            .onAppear {
                focused = true
            }
        }
    }

    private func runAgent() {
        guard !input.isEmpty else { return }
        isLoading = true
        output = ""

        AgentClient.shared.sendQuery(input) { result in
            DispatchQueue.main.async {
                self.output = result
                self.isLoading = false
            }
        }
    }
}
