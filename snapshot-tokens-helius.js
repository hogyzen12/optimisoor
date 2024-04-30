const { writeFileSync } = require("fs");
const fetch = require("node-fetch");

const url = `https://mainnet.helius-rpc.com/?api-key=5adcfebf-b520-4bcd-92ee-b4861e5e7b5b`;

const getTokenAccounts = async () => {
    let tokenAccounts = [];

    let cursor;
    while (true) {
        let params = {
            limit: 1000,
            mint: "jucy5XJ76pHVvtPZb5TKRcGQExkwit2P5s4vY8UzmpC"
        };

        if (cursor !== undefined) {
            params.cursor = cursor;
        }

        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                jsonrpc: "2.0",
                id: "helius-test",
                method: "getTokenAccounts",
                params: params,
            }),
        });

        const data = await response.json();

        // Print the raw response in the terminal for debugging
        console.log(JSON.stringify(data, null, 2));

        if (!data.result || data.result.token_accounts.length === 0) {
            console.log("No more results");
            break;
        }

        data.result.token_accounts.forEach((account) => {
            tokenAccounts.push({
                owner: account.owner,
                amount: account.amount
            });
        });

        cursor = data.result.cursor;
    }
    
    // Save detailed account info in a JSON file
    writeFileSync("tokenAccounts.json", JSON.stringify(tokenAccounts, null, 2));
}

getTokenAccounts();
