// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract GPURentalBase is ReentrancyGuard, Ownable {
    struct GPU {
        address payable owner;
        string specs;
        uint256 pricePerComputeUnit;
        bool isAvailable;
    }

    struct TrainingSession {
        address aggregatorNode;
        string parameterHash;
        bool isCompleted;
    }

    GPU[] public gpus;
    uint256 public platformCommissionPercent = 2;
    mapping(uint256 => TrainingSession) public sessions;
    mapping(address => uint256) public providerReputation;

    event GPURented(uint256 indexed gpuId, address indexed renter, uint256 computeUnits, uint256 totalCost);
    event GPUCreated(uint256 indexed gpuId, address owner, string specs, uint256 pricePerComputeUnit);
    event GPUSpecsUpdated(uint256 indexed gpuId, string specs, uint256 pricePerComputeUnit);
    event PaymentReleased(uint256 indexed gpuId, address indexed provider);
    event TrainingStarted(uint256 indexed sessionId, address indexed aggregatorNode, string parameterHash);
    event TrainingCompleted(uint256 indexed sessionId, bool isSuccess);

    constructor(address initialOwner) Ownable(initialOwner) {
        transferOwnership(initialOwner);
    }

    function listGPUs(uint256 startIndex, uint256 pageSize) external view returns (GPU[] memory) {
        GPU[] memory page = new GPU[](pageSize);
        for (uint256 i = 0; i < pageSize; i++) {
            if (startIndex + i >= gpus.length) break;
            page[i] = gpus[startIndex + i];
        }
        return page;
    }

    function updateGPUSpecs(uint256 gpuId, string memory _specs, uint256 _newPrice) external onlyOwner {
        require(gpus[gpuId].owner != address(0), "GPU does not exist");
        gpus[gpuId].specs = _specs;
        gpus[gpuId].pricePerComputeUnit = _newPrice;
        emit GPUSpecsUpdated(gpuId, _specs, _newPrice);
    }

    function rentGPU(uint256 gpuId, uint256 computeUnits) external payable nonReentrant {
        require(gpus[gpuId].isAvailable, "GPU not available");
        require(msg.value >= gpus[gpuId].pricePerComputeUnit * computeUnits, "Insufficient payment");

        uint256 totalCost = gpus[gpuId].pricePerComputeUnit * computeUnits;
        uint256 platformCommission = totalCost * platformCommissionPercent / 100;
        uint256 paymentToProvider = totalCost - platformCommission;

        gpus[gpuId].isAvailable = false;

        safeTransfer(gpus[gpuId].owner, paymentToProvider);
        safeTransfer(payable(owner()), platformCommission);

        emit GPURented(gpuId, msg.sender, computeUnits, msg.value);
    }

    function releaseGPU(uint256 gpuId) external nonReentrant {
        require(!gpus[gpuId].isAvailable, "GPU not rented");
        gpus[gpuId].isAvailable = true;
        emit PaymentReleased(gpuId, gpus[gpuId].owner);
    }

    function startTrainingSession(uint256 gpuId, string memory _parameterHash) external returns (uint256, uint256) {
        require(!gpus[gpuId].isAvailable, "GPU must be rented first");
        uint256 sessionId = uint256(keccak256(abi.encodePacked(block.timestamp, msg.sender, gpuId)));
        sessions[sessionId] = TrainingSession(msg.sender, _parameterHash, false);
        emit TrainingStarted(sessionId, msg.sender, _parameterHash);
        
        // Return session ID and the reputation of the GPU's owner
        uint256 reputation = providerReputation[gpus[gpuId].owner];
        return (sessionId, reputation);
    }

    function updateTrainingSession(uint256 sessionId, string memory _parameterHash) external {
        require(sessions[sessionId].aggregatorNode == msg.sender, "Only aggregator node can update session");
        sessions[sessionId].parameterHash = _parameterHash;
    }

    function completeTrainingSession(uint256 sessionId, bool isSuccess) external {
        require(!sessions[sessionId].isCompleted, "Session already completed");
        sessions[sessionId].isCompleted = true;
        if (isSuccess) {
            providerReputation[sessions[sessionId].aggregatorNode]++;
        }
        emit TrainingCompleted(sessionId, isSuccess);
    }

    function safeTransfer(address payable _to, uint256 _amount) private {
        (bool success, ) = _to.call{value: _amount}("");
        require(success, "Transfer failed");
    }
}
