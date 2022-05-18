// SPDX-License-Identifier: MIT
pragma solidity >=0.8.0;

import "forge-std/Test.sol";

contract ParserTest is Test {
    struct AdapterData {
        string contractName;
        bytes constructorParams;
        string[] tokens;
        bool isUnderquoting;
    }

    function testParse() public {
        string[] memory inputs = new string[](6);
        inputs[0] = "python3";
        inputs[1] = "scripts/adapters.py";
        inputs[2] = "--chain_id";
        inputs[3] = "1";
        inputs[4] = "--fn";
        inputs[5] = "test/adapters.json";
        bytes memory res = vm.ffi(inputs);

        (, bytes[] memory adapters) = abi.decode(res, (uint256, bytes[]));
        for (uint256 i = 0; i < adapters.length; ++i) {
            (string memory _c, string memory name, bytes memory args, string[] memory tokens, bool underquote) = abi
            .decode(adapters[i], (string, string, bytes, string[], bool));

            emit log_string(_c);
            emit log_string(name);
            if (keccak256(bytes(_c)) == keccak256("UniswapV2Adapter")) {
                (string memory _name, uint256 _gas, address _factory, bytes32 _hash, uint256 _fee) = abi.decode(
                    args,
                    (string, uint256, address, bytes32, uint256)
                );
                emit log_named_string("Name", _name);
                emit log_named_uint("Gas", _gas);
                emit log_named_address("Factory", _factory);
                emit log_named_bytes32("Hash", _hash);
                emit log_named_uint("Fee", _fee);
            } else {
                emit log_bytes(args);
            }

            emit log_named_uint("Length", tokens.length);
            for (uint256 j = 0; j < tokens.length; ++j) {
                emit log_string(tokens[j]);
            }
            emit log_string(underquote ? "True" : "False");
        }
    }
}
