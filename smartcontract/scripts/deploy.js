require('dotenv').config();

async function main() {
    const [deployer] = await ethers.getSigners(); // Get the account to deploy the contract
    console.log("Deploying contracts with the account:", deployer.address);
  
    const Contract = await ethers.getContractFactory("GPURental");
    const contract = await Contract.deploy(); // Deploy the contract
  
    console.log("Contract deployed to:", contract.address);
  }
  
  main()
    .then(() => process.exit(0))
    .catch((error) => {
      console.error(error);
      process.exit(1);
    });
  