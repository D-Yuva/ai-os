import Foundation

func runAgent(_ text: String) {
    let url = URL(string: "http://127.0.0.1:8000/query")!
    
    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    request.addValue("application/json", forHTTPHeaderField: "Content-Type")
    request.httpBody = try? JSONSerialization.data(
        withJSONObject: ["text": text]
    )

    URLSession.shared.dataTask(with: request) { _, response, error in
        if let error = error {
            DispatchQueue.main.async {
                print("❌ Backend not reachable:", error.localizedDescription)
            }
        }
    }.resume()
}


