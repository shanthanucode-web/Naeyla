use std::net::{SocketAddr, TcpStream};
use std::path::PathBuf;
use std::process::{Command, Stdio};
use std::time::Duration;
use tauri::Manager;
use tauri_plugin_global_shortcut::GlobalShortcutExt;

fn find_backend_script() -> Option<PathBuf> {
    if let Ok(script) = std::env::var("NAEYLA_BACKEND_SCRIPT") {
        let candidate = PathBuf::from(script);
        if candidate.exists() {
            return Some(candidate);
        }
    }

    if let Ok(root) = std::env::var("NAEYLA_ROOT") {
        let candidate = PathBuf::from(root)
            .join("tauri-app/naeyla-native/src-tauri/scripts/start_backend.sh");
        if candidate.exists() {
            return Some(candidate);
        }
    }

    let manifest_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    let candidate = manifest_dir.join("scripts").join("start_backend.sh");
    if candidate.exists() {
        return Some(candidate);
    }

    if let Ok(mut dir) = std::env::current_dir() {
        for _ in 0..6 {
            let candidate = dir.join("src-tauri/scripts/start_backend.sh");
            if candidate.exists() {
                return Some(candidate);
            }
            if !dir.pop() {
                break;
            }
        }
    }

    None
}

fn start_backend() -> Result<(), String> {
    let Some(script) = find_backend_script() else {
        return Err("NAEYLA backend auto-start: script not found.".to_string());
    };

    Command::new("bash")
        .arg(script)
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn()
        .map_err(|err| format!("Failed to spawn backend: {err}"))?;

    Ok(())
}

fn backend_is_running() -> bool {
    let addr: SocketAddr = "127.0.0.1:7861".parse().unwrap();
    TcpStream::connect_timeout(&addr, Duration::from_millis(200)).is_ok()
}

#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[tauri::command]
fn ensure_backend() -> Result<bool, String> {
    if backend_is_running() {
        return Ok(true);
    }

    start_backend()?;

    for _ in 0..20 {
        if backend_is_running() {
            return Ok(true);
        }
        std::thread::sleep(Duration::from_millis(500));
    }

    Ok(false)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_global_shortcut::Builder::new().build())
        .setup(|app| {
            let handle = app.handle().clone();

            // Best-effort backend auto-start for native app (runs in background to avoid blocking setup)
            std::thread::spawn(|| { let _ = ensure_backend(); });
            
            // Register global shortcut to toggle window visibility
            #[allow(deprecated)]
            app.global_shortcut().register("CmdOrCtrl+Shift+N")?;

            app.global_shortcut().on_shortcut("CmdOrCtrl+Shift+N", move |_app, _shortcut, _event| {
                if let Some(window) = handle.get_webview_window("main") {
                    let _ = if window.is_visible().unwrap_or(false) {
                        window.hide()
                    } else {
                        window.show()
                    };
                }
            })?;
            
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![greet, ensure_backend])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
