require("@nomicfoundation/hardhat-toolbox");
require('dotenv').config();

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: "0.8.24",
  networks: {
    // mainnet: {
    //   url: `https://eth-mainnet.g.alchemy.com/v2/vKl8FZyN4g9TujER9bR8esozcq0oCb8p`
    // },
    testnet: {
      url: `https://eth-sepolia.g.alchemy.com/v2/y3NM9NRZepDsjduwf9SDk-HYZLboAMDW`,
      accounts: {
        mnemonic: process.env.TEST_NET_ACCOUNT_MNEMONIC,
        gasPrice: 20000000000 // 20 Gwei
      }
    }
  }
};
