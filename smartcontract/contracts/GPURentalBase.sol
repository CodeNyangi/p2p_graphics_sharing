// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

abstract contract GPURentalBase is ReentrancyGuard, Ownable {
    struct GPU {
        address payable owner;
        string specs;
        uint256 pricePerComputeUnit;
        bool isAvailable;
        string currentTaskModel; // Name of the model currently being trained
        string currentDataset;
    }

    struct TrainingSession {
        uint256 currentEpoch;
        address aggregatorNode;
        string parameterHash;
    }


    GPU[] public gpus;
    uint256 public platformCommissionPercent = 2;
    mapping(uint256 => TrainingSession) public sessions;
    mapping(uint256 => uint256) public taskToRentalStartTime;
    mapping(address => uint256) public providerReputation;

    event GPURented(uint256 indexed gpuId, address indexed renter, uint256 computeUnits, uint256 totalCost, string model, string dataset);
    event ModelAssigned(uint256 indexed gpuId, string modelName);
    event GPUListed(uint256 indexed gpuId, string specs, uint256 pricePerComputeUnit);
    event PaymentReleased(uint256 indexed gpuId, address indexed provider);
    event CommissionAdjusted(uint256 newCommissionPercent);
    event TrainingUpdated(uint256 indexed sessionId, uint256 epoch, string parameterHash);


    // Constructor that accepts an initial owner address
    constructor(address initialOwner) Ownable(initialOwner) {
        // You can include additional initializations here if necessary
    }

    function assignModel(uint256 gpuId, string memory modelName) external {
        gpus[gpuId].currentTaskModel = modelName;
        emit ModelAssigned(gpuId, modelName);
    }

     function startTrainingSession(uint256 gpuId) external returns (uint256) {
        require(gpus[gpuId].isAvailable, "GPU must be rented first");
        uint256 sessionId = uint256(keccak256(abi.encodePacked(block.timestamp, msg.sender, gpuId)));
        sessions[sessionId] = TrainingSession(0, msg.sender, "");
        return sessionId;
    }

    function updateTraining(uint256 sessionId, uint256 epoch, string memory parameterHash) external {
        TrainingSession storage session = sessions[sessionId];
        require(msg.sender == session.aggregatorNode, "Only the aggregator node can update training");
        session.currentEpoch = epoch;
        session.parameterHash = parameterHash;
        emit TrainingUpdated(sessionId, epoch, parameterHash);
    }

    function changeAggregator(uint256 sessionId, address newAggregator) external onlyOwner {
        TrainingSession storage session = sessions[sessionId];
        session.aggregatorNode = newAggregator;
    }

    function listGPU(string memory _specs, uint256 _pricePerComputeUnit) external {
        gpus.push(GPU(payable(msg.sender), _specs, _pricePerComputeUnit, true, "", ""));
        emit GPUListed(gpus.length - 1, _specs, _pricePerComputeUnit);
    }


    function rentGPU(uint256 _gpuId, uint256 _computeUnits, string memory _model, string memory _dataset) external payable nonReentrant {
        GPU storage gpu = gpus[_gpuId];
        require(gpu.isAvailable, "GPU not available");
        require(msg.value >= gpu.pricePerComputeUnit * _computeUnits, "Insufficient payment");

        uint256 totalCost = gpu.pricePerComputeUnit * _computeUnits;
        uint256 platformCommission = (totalCost * platformCommissionPercent) / 100;
        uint256 paymentToProvider = totalCost - platformCommission;

        gpu.isAvailable = false;
        taskToRentalStartTime[_gpuId] = block.timestamp;
        
        safeTransfer(gpu.owner, paymentToProvider);
        safeTransfer(payable(owner()), platformCommission);

        gpus[_gpuId].currentTaskModel = _model;
        gpus[_gpuId].currentDataset = _dataset;

        emit GPURented(_gpuId, msg.sender, _computeUnits, msg.value, _model, _dataset);
    }

    function releaseGPU(uint256 _gpuId) external nonReentrant {
        require(!gpus[_gpuId].isAvailable, "GPU not rented");
        require(block.timestamp >= taskToRentalStartTime[_gpuId] + 1 hours, "Rental period not ended");

        gpus[_gpuId].isAvailable = true;
        providerReputation[gpus[_gpuId].owner]++;

        emit PaymentReleased(_gpuId, gpus[_gpuId].owner);
    }

    function updateGPUComputePrice(uint256 _gpuId, uint256 _newPrice) external onlyOwner {
        GPU storage gpu = gpus[_gpuId];
        gpu.pricePerComputeUnit = _newPrice;
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
