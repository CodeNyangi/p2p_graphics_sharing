# P2P Graphics Resource Sharing System

## Introduction

This project implements a peer-to-peer (P2P) system for sharing graphics processing resources. It enables users to offer their unused graphics card capabilities to others who need additional processing power, facilitating a decentralized network of resource sharing.

## Features

- Peer discovery for connecting users within the P2P network.
- Resource listing to advertise available graphics processing units (GPUs).
- Direct peer communication for efficient resource sharing.
- Secure registration and resource request system.

## Prerequisites

- Rust: Ensure you have the latest stable Rust installed on your machine.
- Cargo: Comes with Rust, used for dependency management and building the project.


## Installation

1. Clone the repository:
```bash
git clone https://github.com/popeyeGOEL/p2p-graphics-resource-sharing.git
cd p2p-graphics-resource-sharing
cargo build --release
```

## Usage

### Starting the Server

To start the server (discovery service), run:

```bash
cargo run --bin server
cargo run --bin client -- --server-url http://localhost:8080
```

## Contributing
We welcome contributions to this project! Please consider the following ways to contribute:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer


