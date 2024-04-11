async function main() {
  const [deployer] = await ethers.getSigners();
  
  console.log("Deploying contracts with the account:", deployer.address);
  
  const GPURental = await ethers.getContractFactory("GPURental");
  const gpuRental = await GPURental.deploy(deployer.address); // Pass the deployer's address as the initial owner

  console.log("GPURental deployed to:", gpuRental.address);
}

main()
  .then(() => process.exit(0))
  .catch(error => {
      console.error(error);
      process.exit(1);
  });
