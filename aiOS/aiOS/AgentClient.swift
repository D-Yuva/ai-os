import Foundation

struct AgentResponse: Decodable {
    let status: String
    let response: String?
    let error: String?
}

final class AgentClient {

    static let shared = AgentClient()

    private init() {}

    func sendQuery(
        _ text: String,
        onResult: @escaping (String) -> Void
    ) {
        guard let url = URL(string: "http://127.0.0.1:8000/query") else {
            return
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let body = ["text": text]
        request.httpBody = try? JSONSerialization.data(withJSONObject: body)

        URLSession.shared.dataTask(with: request) { data, _, error in
            if let error = error {
                DispatchQueue.main.async {
                    onResult("❌ Network error: \(error.localizedDescription)")
                }
                return
            }

            guard let data = data else {
                DispatchQueue.main.async {
                    onResult("❌ No data from backend")
                }
                return
            }

            let decoded = try? JSONDecoder().decode(AgentResponse.self, from: data)

            DispatchQueue.main.async {
                if let response = decoded?.response {
                    onResult(response)
                } else if let err = decoded?.error {
                    onResult("❌ \(err)")
                } else {
                    onResult(decoded?.response ?? "⚠️ No textual response from agent.")
                }
            }
        }
        .resume()
    }
}
