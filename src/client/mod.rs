pub mod sharing;
pub mod consumption;
pub mod communication;
pub mod security;

// Example function to start the client functionalities
pub fn start_client() {
    println!("Starting client...");
    // Initialize client components here
    // E.g., sharing::init(), consumption::init(), etc.
    sharing::init();
    consumption::init();
    communication::init();
    security::init();
}
