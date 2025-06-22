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
          "name": "nim",
          "type": "string"
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
          "name": "tanggalTerbit",
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
          "name": "nim",
          "type": "string"
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
          "name": "tanggalTerbit",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "hashMetadata",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "cidSuratBebasPerpustakaan",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "cidSuratBebasLaboratorium",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "cidSuratBebasKeuangan",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "cidBuktiPenyerahanSkripsi",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "cidSertifikatToefl",
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
          "components": [
            {
              "internalType": "string",
              "name": "nim",
              "type": "string"
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
              "name": "tanggalTerbit",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "hashMetadata",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "cidSuratBebasPerpustakaan",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "cidSuratBebasLaboratorium",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "cidSuratBebasKeuangan",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "cidBuktiPenyerahanSkripsi",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "cidSertifikatToefl",
              "type": "string"
            }
          ],
          "internalType": "struct BlockchainSertifikasi.SertifikatInput",
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
              "name": "tanggalTerbit",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "hashMetadata",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "cidSuratBebasPerpustakaan",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "cidSuratBebasLaboratorium",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "cidSuratBebasKeuangan",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "cidBuktiPenyerahanSkripsi",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "cidSertifikatToefl",
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
          "internalType": "struct BlockchainSertifikasi.Sertifikat",
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
      "name": "getSertifikatByHash",
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
              "name": "tanggalTerbit",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "hashMetadata",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "cidSuratBebasPerpustakaan",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "cidSuratBebasLaboratorium",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "cidSuratBebasKeuangan",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "cidBuktiPenyerahanSkripsi",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "cidSertifikatToefl",
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
          "internalType": "struct BlockchainSertifikasi.Sertifikat",
          "name": "",
          "type": "tuple"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": True
    }
  ]

contract_address = '0xAf31fB072dC37d16F82dfeB082fFBed0E38BE270' # Ganti sesuai alamat kontrak kamu