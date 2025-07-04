contract_abi = [
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": False,
          "internalType": "bytes32",
          "name": "id",
          "type": "bytes32"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "nim",
          "type": "string"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "universitas",
          "type": "string"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "cidDetail",
          "type": "string"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "nomerSertifikat",
          "type": "string"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "hashMetadata",
          "type": "string"
        }
      ],
      "name": "SertifikatDiterbitkan",
      "type": "event"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "name": "allIds",
      "outputs": [
        {
          "internalType": "bytes32",
          "name": "",
          "type": "bytes32"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": True
    },
    {
      "inputs": [
        {
          "internalType": "bytes32",
          "name": "",
          "type": "bytes32"
        }
      ],
      "name": "daftarSertifikat",
      "outputs": [
        {
          "internalType": "bytes32",
          "name": "id",
          "type": "bytes32"
        },
        {
          "internalType": "string",
          "name": "nim",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "universitas",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "cidDetail",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "hashMetadata",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "nomerSertifikat",
          "type": "string"
        },
        {
          "internalType": "uint256",
          "name": "blockNumber",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": True
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        }
      ],
      "name": "idByHashMetadata",
      "outputs": [
        {
          "internalType": "bytes32",
          "name": "",
          "type": "bytes32"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": True
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        }
      ],
      "name": "idByNIM",
      "outputs": [
        {
          "internalType": "bytes32",
          "name": "",
          "type": "bytes32"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": True
    },
    {
      "inputs": [
        {
          "components": [
            {
              "internalType": "string",
              "name": "nim",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "universitas",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "cidDetail",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "hashMetadata",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "nomerSertifikat",
              "type": "string"
            }
          ],
          "internalType": "struct BlockchainSertifikasiPublik.SertifikatInput",
          "name": "_input",
          "type": "tuple"
        }
      ],
      "name": "terbitkanSertifikat",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "getAllId",
      "outputs": [
        {
          "internalType": "bytes32[]",
          "name": "",
          "type": "bytes32[]"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": True
    },
    {
      "inputs": [
        {
          "internalType": "bytes32",
          "name": "id",
          "type": "bytes32"
        }
      ],
      "name": "getSertifikatById",
      "outputs": [
        {
          "components": [
            {
              "internalType": "bytes32",
              "name": "id",
              "type": "bytes32"
            },
            {
              "internalType": "string",
              "name": "nim",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "universitas",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "cidDetail",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "hashMetadata",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "nomerSertifikat",
              "type": "string"
            },
            {
              "internalType": "uint256",
              "name": "blockNumber",
              "type": "uint256"
            }
          ],
          "internalType": "struct BlockchainSertifikasiPublik.Sertifikat",
          "name": "",
          "type": "tuple"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": True
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_hashMetadata",
          "type": "string"
        }
      ],
      "name": "findSertifikatHash",
      "outputs": [
        {
          "components": [
            {
              "internalType": "bytes32",
              "name": "id",
              "type": "bytes32"
            },
            {
              "internalType": "string",
              "name": "nim",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "universitas",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "cidDetail",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "hashMetadata",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "nomerSertifikat",
              "type": "string"
            },
            {
              "internalType": "uint256",
              "name": "blockNumber",
              "type": "uint256"
            }
          ],
          "internalType": "struct BlockchainSertifikasiPublik.Sertifikat",
          "name": "",
          "type": "tuple"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": True
    }
  ]
