import argparse
import json
from typing import Any, Tuple
from eth_abi import encode_single, encode_abi
from web3 import Web3


def handle_param(param: Any) -> Tuple[str, Any]:
    if isinstance(param, bytes):
        return ("bytes", param)
    elif isinstance(param, str):
        if param.startswith("0x"):
            if len(param) == 42:
                return ("address", param)
            else:
                return ("bytes32", bytes.fromhex(param[2:]))
        else:
            return ("string", param)
    else:
        return ("uint256", int(param))


def encode_param(param: Any) -> bytes:
    if isinstance(param, bytes):
        return encode_single("bytes", param)
    elif isinstance(param, str):
        if param.startswith("0x"):
            if len(param) == 42:
                return encode_single("address", param)
            else:
                return encode_single("bytes32", bytes.fromhex(param[2:]))
        else:
            return encode_single("string", param)
    else:
        return encode_single("uint256", int(param))


def encode_params(params: list[Any]) -> bytes:
    _types = []
    _params = []
    for param in params:
        (_type, _param) = handle_param(param)
        _types.append(_type)
        _params.append(_param)
    return encode_abi(_types, _params)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--chain_id", type=int, required=True)
    parser.add_argument("--fn", type=str, required=True)
    args = parser.parse_args()

    f = open(args.fn)
    data = json.load(f)
    f.close()

    chain_id = str(args.chain_id)

    if chain_id not in data:
        print("Unknown chainId")
        exit(1)

    adapters: list[bytes] = []

    for dex, pools in data[chain_id].items():
        for pool_name, pool in pools.items():
            params = encode_params(pool["params"])
            full = encode_abi(("string", "string", "bytes", "string[]", "bool"), (
                pool["contract"], pool["params"][0], params, pool["tokens"], pool["underquote"]))
            adapters.append(full)

    # For whatever reason encode_single("bytes[]", adapters) doesn't encode correctly
    print("0x" + encode_abi(("uint256", "bytes[]"), (0, adapters)).hex())
