pub mod bootstrap;
pub mod directory;
pub mod auth;
pub mod transaction;

// Example function to start the server components
pub fn start_server() {
    println!("Starting server...");
    // Initialize server components here

    bootstrap::init();
    directory::init();
    auth::init();
    transaction::init();

}
