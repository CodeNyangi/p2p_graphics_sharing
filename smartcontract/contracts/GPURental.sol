// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract GPURental {
    address payable public platformOperator;
    uint public commissionPercentage = 2;  // 2% commission
    mapping(uint => address payable) private taskToProvider;  // Maps task IDs to GPU providers
    mapping(uint => uint) public taskBalances;  // Maps task IDs to locked payment amounts

    // Modifiers for access control
    modifier onlyPlatformOperator() {
        require(msg.sender == platformOperator, "Caller is not the platform operator");
        _;
    }

    modifier taskHasBalance(uint taskId) {
        require(taskBalances[taskId] > 0, "Task has no locked funds");
        _;
    }

    constructor() {
        platformOperator = payable(msg.sender);  // The deployer is the platform operator.
    }

    // Event declarations
    event GPUDiscovered(uint taskId, address provider);
    event PaymentLocked(uint taskId, uint amount);
    event ResultsVerified(uint taskId, bool isSuccess);
    event PaymentReleased(uint taskId, uint amountToProvider, uint commissionAmount);

    // Functions
    function discoverGPUs(uint taskId) public onlyPlatformOperator {
        // Real implementation needed for GPU discovery
        emit GPUDiscovered(taskId, address(0x123));  // Placeholder address
    }

    function lockPaymentWithCommission(uint taskId, address payable provider) public payable {
        uint commission = msg.value * commissionPercentage / 100;
        uint amountToLock = msg.value - commission;
        taskBalances[taskId] = amountToLock;
        taskToProvider[taskId] = provider;  // Assign the provider to the task

        emit PaymentLocked(taskId, amountToLock);

        // Immediately transfer the commission to the platform operator
        (bool sent, ) = platformOperator.call{value: commission}("");
        require(sent, "Failed to send commission");
    }

    function verifyResults(uint taskId, bool isSuccess) public onlyPlatformOperator taskHasBalance(taskId) {
        emit ResultsVerified(taskId, isSuccess);
        if (isSuccess) {
            releasePaymentWithCommission(taskId);  // Auto-release funds upon successful verification
        } else {
            // Handle unsuccessful verification, possibly refunding the task submitter
        }
    }

    function releasePaymentWithCommission(uint taskId) private taskHasBalance(taskId) {
        address payable provider = taskToProvider[taskId];
        uint amount = taskBalances[taskId];

        (bool sent, ) = provider.call{value: amount}("");
        require(sent, "Failed to send payment to provider");

        taskBalances[taskId] = 0;  // Clear the locked payment amount

        emit PaymentReleased(taskId, amount, 0);  // Commission already taken during lock
    }
}
