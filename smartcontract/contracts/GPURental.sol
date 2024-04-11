// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./GPURentalBase.sol";

contract GPURental is GPURentalBase {
    // Pass the initial owner to the GPURentalBase constructor
    constructor(address initialOwner) GPURentalBase(initialOwner) {
        // Contract initialization can go here
    }

    // Implementation of the abstract methods or any additional methods
}
