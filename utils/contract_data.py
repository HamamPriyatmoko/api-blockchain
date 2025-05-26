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
          "internalType": "uint256",
          "name": "id",
          "type": "uint256"
        },
        {
          "indexed": False,
          "internalType": "address",
          "name": "penerima",
          "type": "address"
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
      "name": "daftarSertifikat",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "id",
          "type": "uint256"
        },
        {
          "internalType": "address",
          "name": "penerima",
          "type": "address"
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
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "name": "hashByPenerima",
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
      "inputs": [],
      "name": "jumlahSertifikat",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
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
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "name": "sertifikatIdByPenerima",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
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
          "internalType": "address",
          "name": "penerima",
          "type": "address"
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
          "name": "dataHash",
          "type": "string"
        }
      ],
      "name": "terbitkanSertifikat",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "id",
          "type": "uint256"
        }
      ],
      "name": "verifikasiSertifikat",
      "outputs": [
        {
          "internalType": "address",
          "name": "penerima",
          "type": "address"
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
          "internalType": "address",
          "name": "penerima",
          "type": "address"
        }
      ],
      "name": "cekSertifikatByPenerima",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
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
          "internalType": "address",
          "name": "penerima",
          "type": "address"
        }
      ],
      "name": "getHashByPenerima",
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


contract_address = '0x1352E410B9E9ca9423eE476957745F4FAaE04C58' # Ganti sesuai alamat kontrak kamu
