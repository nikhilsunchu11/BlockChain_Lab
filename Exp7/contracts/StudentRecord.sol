// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract StudentRecord {
    string public studentName;
    uint256 public studentRoll;

    constructor(string memory _name, uint256 _roll) {
        studentName = _name;
        studentRoll = _roll;
    }
    function updateName(string memory _name) public {
        studentName = _name;
    }
    function updateRoll(uint256 _roll) public {
        studentRoll = _roll;
    }
}
