const StudentRecord = artifacts.require("StudentRecord");

module.exports = function (deployer) {
  deployer.deploy(StudentRecord, "Nikhil Sunchu", 31);
};
