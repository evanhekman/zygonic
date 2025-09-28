//
//  menuApp.swift
//  menu
//
//  Created by Jerry Zhu on 9/27/25.

import SwiftUI

let SERVER = "http://127.0.0.1:8000/"


@main
struct MenuApp: App {
    @State private var tasks: [AppTask] = {
        // Initialize with loaded tasks
        return loadInitialTasks()
    }()
    @State private var newTaskName: String = ""
    
    var body: some Scene {
        MenuBarExtra {
            VStack(spacing: 0) {
                // Header
                Text("Zygonic")
                    .font(.title2)
                    .fontWeight(.bold)
                    .padding(.bottom, 8)
                
                // Scrollable task list
                ScrollView {
                    LazyVStack(spacing: 0) {
                        ForEach($tasks) { $task in
                            TaskRowView(
                                task: $task,
                                onDelete: { deleteTask(withId: task.id) }  // uses stable view id
                            )
                        }
                    }
                }
                .frame(height: 300) // Fixed height - always 300 points
                
                // Add new task input (fixed at bottom)
                VStack(spacing: 8) {
                    TextField("Enter task name", text: $newTaskName)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                        .onSubmit {
                            addNewTask()
                        }
                    
                    Button(action: {
                        addNewTask()
                    }) {
                        HStack {
                            Spacer()
                            Text("Add New Task")
                                .font(.headline)
                                .foregroundColor(.primary)
                            Spacer()
                        }
                        .padding()
                        .background(Color.gray.opacity(0.1))
                    }
                    .buttonStyle(PlainButtonStyle())
                    .cornerRadius(8)
                }
                .padding(.top, 8)
            }
            .frame(width: 320)
            .padding(.horizontal, 8)
            .padding(.vertical, 8)
        } label: {
            Image("MenuIcon")
        }
        .menuBarExtraStyle(.window)
    }
    
    // MARK: - Database-Ready Functions
    
    /// Load initial tasks when app starts (static function for initialization)
    private static func loadInitialTasks() -> [AppTask] {
        // TODO: Replace with actual database call (async fetch & set in onAppear if desired)
        return []
    }
    
    /// Reload tasks from storage (for refreshing during runtime)
    private func reloadTasks() {
        // TODO: Replace with actual database call
        tasks = Self.loadInitialTasks()
    }
    
    /// Add a new task to storage (optimistic create; API returns UUID)
    @MainActor
    private func addNewTask() {
        let trimmed = newTaskName.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }
        
        // 1) Create optimistic item (no serverId yet)
        let optimistic = createTask(title: trimmed)
        
        // 2) Append to UI immediately
        insertTask(optimistic)
        
        // 3) Clear input
        newTaskName = ""
        
        // 4) Ask API to create; patch in returned UUID
        Task { @MainActor in
            do {
                let created = try await apiCreateTask(title: trimmed)
                if let idx = tasks.firstIndex(where: { $0.id == optimistic.id }) {
                    tasks[idx].serverId = created.content
                }
            } catch {
                // On failure, remove optimistic item (or mark error state)
                tasks.removeAll { $0.id == optimistic.id }
                // TODO: surface an error toast/UI if desired
            }
        }
    }
    
    /// Create a new task with default values (no serverId yet; API will return it)
    private func createTask(title: String) -> AppTask {
        let colors: [Color] = [.blue, .green, .orange, .red, .pink, .mint, .purple, .cyan]
        let randomColor = colors.randomElement() ?? .blue
        
        return AppTask(
            serverId: nil,              // <- API will provide later
            title: title,
            status: .NEW,
            color: randomColor,
            isCompleted: false,
            progress: 0.0
        )
    }
    
    /// Insert a task into storage
    private func insertTask(_ task: AppTask) {
        tasks.append(task)
    }
    
    /// Delete a task by ID (prefers server delete when available)
    @MainActor
    private func deleteTask(withId id: UUID) {
        guard let index = tasks.firstIndex(where: { $0.id == id }) else { return }
        let item = tasks[index]
        
        // Optimistic remove from UI
        tasks.remove(at: index)
        
        // If it exists on the server, also delete remotely
        if let serverId = item.serverId {
            Task {
                try? await apiDeleteTask(id: serverId)
            }
        }
    }
    
    struct CreateTaskResponse: Decodable {
        let statusCode: Int
        let content: Int

        enum CodingKeys: String, CodingKey {
            case statusCode = "status_code"
            case content
        }
    }

    private func apiCreateTask(title: String) async throws -> CreateTaskResponse {
        guard let url = URL(string: SERVER)?.appendingPathComponent("new") else {
            throw URLError(.badURL)
        }
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")
        let body: [String: Any] = [
            "description": title,
            "status": "NEW",
            "progress": 0.0
        ]
        request.httpBody = try JSONSerialization.data(withJSONObject: body)
        let (data, response) = try await URLSession.shared.data(for: request)
        guard let httpResponse = response as? HTTPURLResponse else {
            throw URLError(.badServerResponse)
        }
        guard (200...299).contains(httpResponse.statusCode) else {
            let errorText = String(data: data, encoding: .utf8) ?? "Unknown error"
            throw NSError(domain: "APIError", code: httpResponse.statusCode,
                          userInfo: [NSLocalizedDescriptionKey: errorText])
        }
        return try JSONDecoder().decode(CreateTaskResponse.self, from: data)
    }

    
    // 4) DELETE /delete?task_id=<int>  (no JSON body)
    private func apiDeleteTask(id: Int) async throws {
        guard var comps = URLComponents(string: SERVER) else { throw URLError(.badURL) }
        if comps.path.isEmpty { comps.path = "/" }
        let basePath = comps.path
        comps.path = basePath.appending("delete")
        comps.queryItems = [URLQueryItem(name: "task_id", value: String(id))]
        guard let url = comps.url else { throw URLError(.badURL) }

        var request = URLRequest(url: url)
        request.httpMethod = "DELETE"
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")

        let (_, response) = try await URLSession.shared.data(for: request)
        guard let http = response as? HTTPURLResponse,
              (200...299).contains(http.statusCode) else {
            throw URLError(.badServerResponse)
        }
    }

    
    // MARK: - Color mapping helpers (persist color as hex/string)
    private func colorToHex(_ color: Color) -> String {
        // Minimal placeholder; implement precise RGBA extraction as needed
        // You can map your fixed palette to known hex codes if preferred.
        switch String(describing: color) {
        case "blue": return "#3B82F6"
        case "green": return "#10B981"
        case "orange": return "#F59E0B"
        case "red": return "#EF4444"
        case "pink": return "#EC4899"
        case "mint": return "#99F6E4"
        case "purple": return "#8B5CF6"
        case "cyan": return "#22D3EE"
        default: return "#3B82F6"
        }
    }
}

enum TaskStatus: String, Codable, CaseIterable, Equatable {
    case NEW, STARTED, COMPLETED
}

struct AppTask: Identifiable, Equatable {
    var serverId: Int?
    private let tempId = UUID()
    var id: UUID { tempId }   // used only for SwiftUI diffing
    var title: String
    var status: TaskStatus
    var color: Color
    var isCompleted: Bool
    var progress: Double // 0.0 to 100.0
}

struct TaskRowView: View {
    @Binding var task: AppTask
    let onDelete: () -> Void
    @State private var isAnimating = false
    
    var body: some View {
        HStack(spacing: 8) {
            // Checkbox
            Button(action: {
                withAnimation(.spring(response: 0.3, dampingFraction: 0.6, blendDuration: 0)) {
                    task.isCompleted.toggle()
                    if task.isCompleted {
                        task.progress = 100.0
                        // Trigger completion animation
                        isAnimating = true
                        
                        // Reset animation state after delay
                        DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
                            isAnimating = false
                        }
                    } else if task.progress >= 100 {
                        task.progress = 0
                    }
                    // Optional: fire-and-forget update if serverId exists
                    if let sid = task.serverId {
                        Task {
                            try? await apiUpdateTask(
                                taskId: sid,
                                title: task.title,
                                status: task.status.rawValue,
                                progress: task.progress
                            )
                        }
                    }
                }
            }) {
                Image(systemName: task.isCompleted ? "checkmark.square" : "square")
                    .foregroundColor(task.isCompleted ? .green : .gray)
                    .font(.system(size: 16, weight: .medium))
            }
            .buttonStyle(PlainButtonStyle())
            .frame(width: 24, height: 24)
            
            // Task slider bar with custom drag gesture
            GeometryReader { geometry in
                ZStack {
                    // Background progress bar
                    HStack(spacing: 0) {
                        // Filled portion
                        Rectangle()
                            .fill(task.color)
                            .frame(width: geometry.size.width * (task.progress / 100.0))
                        
                        // Unfilled portion
                        Rectangle()
                            .fill(task.color.opacity(0.2))
                    }
                    .cornerRadius(6)
                    
                    // Task title overlay
                    HStack {
                        VStack(alignment: .leading, spacing: 2) {
                            if task.status != .COMPLETED {
                                Text(task.title)
                                    .font(.system(size: 14, weight: .medium))
                                    .foregroundColor(task.progress < 50 ? .primary : .white)
                            } else {
                                Text("\(task.title) (\(task.status.rawValue))")
                                    .font(.system(size: 14, weight: .medium))
                                    .foregroundColor(.white)
                            }
                        }
                        Spacer()
                        
                        // Progress percentage
                        Text("\(Int(task.progress))%")
                            .font(.system(size: 12, weight: .medium))
                            .foregroundColor(task.progress < 50 ? .primary : .white)
                            .opacity(0.8)
                    }
                    .padding(.leading, 12)
                    .padding(.trailing, 30)
                }
                .gesture(
                    DragGesture(minimumDistance: 0)
                        .onChanged { value in
                            let newProgress = (value.location.x / geometry.size.width) * 100.0
                            task.progress = max(0, min(100, newProgress))
                            task.isCompleted = task.progress >= 100
                            // Optional: persist progress as the user drags (throttle/debounce in real app)
                            if let sid = task.serverId {
                                Task {
                                    try? await apiUpdateTask(
                                        taskId: sid,
                                        title: task.title,
                                        status: task.status.rawValue,
                                        progress: task.progress
                                    )
                                }
                            }
                        }
                )
            }
            .frame(height: 44)
        }
        .overlay(alignment: .trailing) {
            Button(role: .destructive, action: onDelete) {
                Image(systemName: "trash")
                    .font(.system(size: 13, weight: .semibold))
                    .padding(6)                    // decent hit target
            }
            .buttonStyle(PlainButtonStyle())
            .help("Delete task")
            .keyboardShortcut(.delete, modifiers: []) // optional: ⌫ when row is focused
            .padding(.trailing, 2)
        }
        .padding(.vertical, 1)
        .scaleEffect(isAnimating ? 1.05 : 1.0)
        .opacity(task.isCompleted ? (isAnimating ? 0.5 : 0.7) : 1.0)
        .animation(.easeInOut(duration: 0.15), value: isAnimating)
    }
    
    // Local helpers to avoid referencing parent scope
    private func colorToHex(_ color: Color) -> String {
        switch String(describing: color) {
        case "blue": return "#3B82F6"
        case "green": return "#10B981"
        case "orange": return "#F59E0B"
        case "red": return "#EF4444"
        case "pink": return "#EC4899"
        case "mint": return "#99F6E4"
        case "purple": return "#8B5CF6"
        case "cyan": return "#22D3EE"
        default: return "#3B82F6"
        }
    }
    
    struct TaskRequest: Codable {
        let description: String
        let status: String
        let progress: Double
    }

    struct UpdateTaskResponse: Codable {
        let message: String
        let task_id: Int
    }

    struct ApiError: Codable, Error {
        let detail: String
    }

    private func apiUpdateTask(
        taskId: Int,
        title: String,
        status: String = "NEW",
        progress: Double = 0.0
    ) async throws -> UpdateTaskResponse {
        // Build URL: SERVER + "/update?task_id=<id>"
        guard var comps = URLComponents(string: SERVER) else { throw URLError(.badURL) }
        if comps.path.isEmpty { comps.path = "/" }
        let basePath = comps.path
        comps.path = basePath.appending("update")
        comps.queryItems = [URLQueryItem(name: "task_id", value: String(taskId))]
        guard let url = comps.url else { throw URLError(.badURL) }

        // Build request body
        let body = TaskRequest(description: title, status: status, progress: progress)

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(body)

        // Execute
        let (data, response) = try await URLSession.shared.data(for: request)
        guard let http = response as? HTTPURLResponse else { throw URLError(.badServerResponse) }

        // Happy path
        if (200...299).contains(http.statusCode) {
            return try JSONDecoder().decode(UpdateTaskResponse.self, from: data)
        }

        // Try to surface FastAPI error bodies (404/500)
        if let apiError = try? JSONDecoder().decode(ApiError.self, from: data) {
            throw NSError(
                domain: "APIError",
                code: http.statusCode,
                userInfo: [NSLocalizedDescriptionKey: apiError.detail]
            )
        }

        // Fallback with raw text
        let text = String(data: data, encoding: .utf8) ?? "Unknown error"
        throw NSError(domain: "APIError", code: http.statusCode,
                      userInfo: [NSLocalizedDescriptionKey: text])
    }
}
