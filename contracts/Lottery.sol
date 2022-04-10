// SPDX-License-Identifier: MIT
pragma solidity ^0.6.6;

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.6/VRFConsumerBase.sol";

contract Lottery is VRFConsumerBase, Ownable {
    // VRFConsumerBase, can use vrf generate random functions
    // Ownable, an openzeppelin prefix, to have an owner
    // https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/access/Ownable.sol

    address payable[] public players; // players is a public address array to store player address
    address payable public recentWinner; // recent winner address
    uint256 public usdEntryFee;
    uint256 public randomness; // recent generated random number
    AggregatorV3Interface internal ethUsdPriceFeed; // a price feed
    // LOTTERY_STATE have 3 states, 0, 1, and 2. matching open, closed,and calculating_winner
    // LOTTERY_STATE is a defined type.
    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }
    // define a LOTTERY_STATE type variable lottery_state
    LOTTERY_STATE public lottery_state;
    uint256 public fee;
    bytes32 public keyhash; // each chainlink price feed on different networks has a unique keyhash
    event RequestedRandomness(bytes32 requestId);

    // an event is like a print onchain. this event will be generated when requestRandomness is called

    constructor(
        address _priceFeedAddress,
        address _vrfCoordinator,
        address _link,
        uint256 _fee,
        bytes32 _keyhash
    ) public VRFConsumerBase(_vrfCoordinator, _link) {
        usdEntryFee = 50 * (10**(18));
        ethUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress);
        lottery_state = LOTTERY_STATE.CLOSED;
        fee = _fee;
        keyhash = _keyhash;
    }

    function enter() public payable {
        require(lottery_state == LOTTERY_STATE.OPEN); // needs to be open
        require(msg.value >= getEntranceFee(), "Not enough ETH!");
        // $50 minimum
        players.push(msg.sender);
    }

    function getEntranceFee() public view returns (uint256) {
        (, int256 price, , , ) = ethUsdPriceFeed.latestRoundData();
        // latestRoundData returns 5 different values, which we need the price
        // feed returns 8 decimals so add 10 decimals to become 18 decimals
        uint256 adjustedPrice = uint256(price) * (10**10);
        uint256 costToEnter = (usdEntryFee * 10**18) / adjustedPrice;
        return costToEnter;
    }

    function startLottery() public onlyOwner {
        // only owner can run it
        require(
            lottery_state == LOTTERY_STATE.CLOSED,
            "Cannot start a new lottery yet"
        );
        lottery_state = LOTTERY_STATE.OPEN;
    }

    // 获取随机数 关闭Lottery. 实际的关闭发生在fulfillRandomness函数中, end函数只用于调用requestRandomness
    function endLottery() public onlyOwner {
        lottery_state = LOTTERY_STATE.CALCULATING_WINNER;
        // requestRandomness from VRFCoordinator
        // requestRandomness函数的定义可在VRFConsumerBase.sol中找到
        bytes32 requestId = requestRandomness(keyhash, fee);
        // call requestRandomness
        emit RequestedRandomness(requestId);
    }

    // 向chainlink请求随机数后, VRFCoordinator会调用rawfulfillrandomness, 然后调用这个函数
    // fulfillrandomness用于收到随机数后利用该随机数执行一些操作
    function fulfillRandomness(bytes32 _requestId, uint256 _randomness)
        internal
        override
    {
        require(
            lottery_state == LOTTERY_STATE.CALCULATING_WINNER,
            "You are not there yet"
        );
        require(_randomness > 0, "random not found");
        uint256 indexOfWinner = _randomness % players.length;
        recentWinner = players[indexOfWinner]; // generate winner
        recentWinner.transfer(address(this).balance); // transfer all fund to winner
        // reset
        players = new address payable[](0);
        lottery_state = LOTTERY_STATE.CLOSED;
        randomness = _randomness;
    }
}
