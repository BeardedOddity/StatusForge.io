// === STATUSFORGE DIAGNOSTIC SUITE ===
// Run this via terminal using: node test_engine.js

async function runTests() {
    console.log("🧪 Initiating StatusForge Engine Diagnostics...\n");

    let forgeToken = "";

    // TEST 1: Check if the Engine is breathing
    try {
        process.stdout.write("-> [Test 1] Pinging Engine /status... ");
        const statusRes = await fetch("http://127.0.0.1:5050/status");
        if (statusRes.ok) {
            console.log("✅ PASS (Engine is live)");
        } else {
            throw new Error(`HTTP ${statusRes.status}`);
        }
    } catch (e) {
        console.log("❌ FAIL");
        console.error("   CRITICAL: Engine is offline or unreachable. Run 'npm start' first.");
        return; // Halt tests if engine is dead
    }

    // TEST 2: Retrieve the WIDGET_TOKEN
    try {
        process.stdout.write("-> [Test 2] Retrieving Security Token... ");
        const tokenRes = await fetch("http://127.0.0.1:5050/get-token");
        const tokenData = await tokenRes.json();
        
        if (tokenData.token && tokenData.token.length > 5) {
            forgeToken = tokenData.token;
            console.log("✅ PASS (Token acquired)");
        } else {
            throw new Error("Invalid token format returned.");
        }
    } catch (e) {
        console.log("❌ FAIL");
        console.error("   Cannot retrieve token. Engine may be corrupted.");
        return;
    }

    // TEST 3: Attempt a malicious hijack (No Token)
    try {
        process.stdout.write("-> [Test 3] Testing Security Boundary... ");
        // We purposefully omit the 'X-Forge-Token' header here to ensure it gets blocked
        const rejectRes = await fetch("http://127.0.0.1:5050/settings", { 
            method: 'POST', 
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ idle_category: "HACKED" }) 
        });
        
        if (rejectRes.status === 401) {
            console.log("✅ PASS (Engine successfully blocked unauthorized hijack)");
        } else {
            console.log("❌ FAIL");
            console.error(`   SECURITY BREACH: Expected HTTP 401, but got HTTP ${rejectRes.status}.`);
        }
    } catch (e) {
        console.log("❌ FAIL (Network error)");
    }

    // TEST 4: Securely push and verify Settings
    try {
        process.stdout.write("-> [Test 4] Committing and Verifying Settings... ");
        
        // Randomize a value to ensure we are reading fresh data, not cached data
        const randomPollRate = Math.floor(Math.random() * 15) + 1;
        
        const payload = {
            auto_push: false,
            safe_mode: true,
            idle_category: "Diagnostic Mode",
            sb_port: 8080,
            widget_poll_rate: randomPollRate,
            widget_fade_timer: 10
        };

        // 1. Post new settings
        const saveRes = await fetch("http://127.0.0.1:5050/settings", {
            method: "POST",
            headers: { 
                "Content-Type": "application/json",
                "X-Forge-Token": forgeToken // Authorized Request
            },
            body: JSON.stringify(payload)
        });

        if (!saveRes.ok) throw new Error(`Save failed: HTTP ${saveRes.status}`);

        // 2. Fetch them back to verify they were written to disk
        const verifyRes = await fetch("http://127.0.0.1:5050/settings", {
            headers: { "X-Forge-Token": forgeToken }
        });
        const verifyData = await verifyRes.json();

        if (verifyData.widget_poll_rate === randomPollRate && verifyData.idle_category === "Diagnostic Mode") {
            console.log("✅ PASS (Data securely written to vault and read back)");
        } else {
            console.log("❌ FAIL");
            console.error("   Settings mismatch! Data did not save to disk correctly.");
        }

    } catch (e) {
        console.log("❌ FAIL");
        console.error("   ", e.message);
    }

    console.log("\n🏁 Diagnostics Complete.");
}

runTests();