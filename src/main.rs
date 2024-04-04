use std::string::String;

mod server;
mod client;

fn main() {
    // This is a simplified example. In a real application, you'd use a command-line argument parser.
    let args: Vec<String> = std::env::args().collect();
    if args.len() > 1 {
        match args[1].as_str() {
            "server" => server::start_server(),
            "client" => client::start_client(),
            _ => println!("Usage: gpu_p2p_sharing [server|client]"),
        }
    } else {
        println!("Usage: gpu_p2p_sharing [server|client]");
    }
}
