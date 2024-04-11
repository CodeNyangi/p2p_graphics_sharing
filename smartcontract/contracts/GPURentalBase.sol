// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

abstract contract GPURentalBase is ReentrancyGuard, Ownable {
    struct GPU {
        address payable owner;
        string specs;
        uint256 pricePerHour;
        bool isAvailable;
    }

    GPU[] public gpus;
    uint256 public platformCommissionPercent = 2;

    mapping(uint256 => uint256) public taskToRentalStartTime;
    mapping(address => uint256) public providerReputation;

    event GPUListed(uint256 indexed gpuId, string specs, uint256 pricePerHour);
    event GPURented(uint256 indexed gpuId, address indexed renter, uint256 durationHours, uint256 totalCost);
    event PaymentReleased(uint256 indexed gpuId, address indexed provider);
    event CommissionAdjusted(uint256 newCommissionPercent);

    // Constructor that accepts an initial owner address
    constructor(address initialOwner) Ownable(initialOwner) {
        // You can include additional initializations here if necessary
    }

    function listGPU(string memory _specs, uint256 _pricePerHour) external {
        gpus.push(GPU(payable(msg.sender), _specs, _pricePerHour, true));
        emit GPUListed(gpus.length - 1, _specs, _pricePerHour);
    }

    function rentGPU(uint256 _gpuId, uint256 _durationHours) external payable nonReentrant {
        GPU storage gpu = gpus[_gpuId];
        require(gpu.isAvailable, "GPU not available");
        require(msg.value >= gpu.pricePerHour * _durationHours, "Insufficient payment");

        uint256 totalCost = gpu.pricePerHour * _durationHours;
        uint256 platformCommission = (totalCost * platformCommissionPercent) / 100;
        uint256 paymentToProvider = totalCost - platformCommission;

        gpu.isAvailable = false;
        taskToRentalStartTime[_gpuId] = block.timestamp;
        
        safeTransfer(gpu.owner, paymentToProvider);
        safeTransfer(payable(owner()), platformCommission);

        emit GPURented(_gpuId, msg.sender, _durationHours, totalCost);
    }

    function releaseGPU(uint256 _gpuId) external nonReentrant {
        require(!gpus[_gpuId].isAvailable, "GPU not rented");
        require(block.timestamp >= taskToRentalStartTime[_gpuId] + 1 hours, "Rental period not ended");

        gpus[_gpuId].isAvailable = true;
        providerReputation[gpus[_gpuId].owner]++;

        emit PaymentReleased(_gpuId, gpus[_gpuId].owner);
    }

    function adjustPlatformCommission(uint256 _newCommission) external onlyOwner {
        require(_newCommission < 100, "Commission too high");
        platformCommissionPercent = _newCommission;
        emit CommissionAdjusted(_newCommission);
    }

    function getTotalGPUs() external view returns (uint256) {
        return gpus.length;
    }

    // New helper function for safer Ether transfers
    function safeTransfer(address payable _to, uint256 _amount) private {
        (bool success, ) = _to.call{value: _amount}("");
        require(success, "Transfer failed");
    }
}
