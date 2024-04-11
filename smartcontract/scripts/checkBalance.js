require('dotenv').config();
const { ethers } = require("hardhat");

async function main() {
  const account = process.env.TEST_NET_ACCOUNT_ADDRESS; // Replace with the actual address
  const balance = await ethers.provider.getBalance(account);
  console.log(`Balance of ${account}:`, balance, 'ETH');
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
