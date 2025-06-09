contract_abi = [
    {
      "inputs": [],
      "stateMutability": "nonpayable",
      "type": "constructor"
    },
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
          "name": "nama",
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
          "name": "jurusan",
          "type": "string"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "sertifikatToefl",
          "type": "string"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "sertifikatBTA",
          "type": "string"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "sertifikatSKP",
          "type": "string"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "tanggal",
          "type": "string"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "dataHash",
          "type": "string"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "urlCid",
          "type": "string"
        },
        {
          "indexed": False,
          "internalType": "uint256",
          "name": "blockNumber",
          "type": "uint256"
        }
      ],
      "name": "SertifikatDiterbitkan",
      "type": "event"
    },
    {
      "inputs": [],
      "name": "admin",
      "outputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": True
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
          "name": "nama",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "universitas",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "jurusan",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "sertifikatToefl",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "sertifikatBTA",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "sertifikatSKP",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "tanggal",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "urlCid",
          "type": "string"
        },
        {
          "internalType": "uint256",
          "name": "blockNumber",
          "type": "uint256"
        },
        {
          "internalType": "bool",
          "name": "valid",
          "type": "bool"
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
      "name": "hashById",
      "outputs": [
        {
          "internalType": "string",
          "name": "",
          "type": "string"
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
          "name": "nama",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "universitas",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "jurusan",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "sertifikatToefl",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "sertifikatBTA",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "sertifikatSKP",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "tanggal",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "dataHash",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "urlCid",
          "type": "string"
        }
      ],
      "name": "terbitkanSertifikat",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "getAllIds",
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
      "name": "getSertifikat",
      "outputs": [
        {
          "internalType": "string",
          "name": "nama",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "universitas",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "jurusan",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "sertifikatToefl",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "sertifikatBTA",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "sertifikatSKP",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "tanggal",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "urlCid",
          "type": "string"
        },
        {
          "internalType": "uint256",
          "name": "blockNumber",
          "type": "uint256"
        },
        {
          "internalType": "bool",
          "name": "valid",
          "type": "bool"
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
      "name": "getHashById",
      "outputs": [
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": True
    }
  ]

contract_address = '0x6CfcD5270680863aaBa6BC7B421B07AdC235fC79' # Ganti sesuai alamat kontrak kamu