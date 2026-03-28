const https = require("https");

const RESEND_API_KEY = process.env.RESEND_API_KEY;
const SEGMENT_ID = process.env.RESEND_SEGMENT_ID;

function resendRequest(path, body) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify(body);
    const req = https.request(
      {
        hostname: "api.resend.com",
        path,
        method: "POST",
        headers: {
          Authorization: `Bearer ${RESEND_API_KEY}`,
          "Content-Type": "application/json",
          "Content-Length": data.length,
        },
      },
      (res) => {
        let body = "";
        res.on("data", (chunk) => (body += chunk));
        res.on("end", () => {
          if (res.statusCode >= 400) {
            reject(new Error(`Resend API ${res.statusCode}: ${body}`));
          } else {
            resolve(JSON.parse(body));
          }
        });
      }
    );
    req.on("error", reject);
    req.write(data);
    req.end();
  });
}

exports.handler = async (event) => {
  if (event.httpMethod !== "POST") {
    return { statusCode: 405, body: "Method not allowed" };
  }

  if (!RESEND_API_KEY || !SEGMENT_ID) {
    return { statusCode: 500, body: "Server misconfigured" };
  }

  let email;
  try {
    const params = new URLSearchParams(event.body);
    email = params.get("email");
  } catch {
    return { statusCode: 400, body: "Invalid request" };
  }

  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return { statusCode: 400, body: "Invalid email address" };
  }

  // Honeypot check
  try {
    const params = new URLSearchParams(event.body);
    if (params.get("bot-field")) {
      return { statusCode: 302, headers: { Location: "/subscribed/" }, body: "" };
    }
  } catch {}

  try {
    await resendRequest("/contacts", {
      email,
      unsubscribed: false,
      segments: [{ id: SEGMENT_ID }],
    });
  } catch (err) {
    console.error("Failed to create contact:", err.message);
    return { statusCode: 500, body: "Subscription failed. Please try again." };
  }

  return {
    statusCode: 302,
    headers: { Location: "/subscribed/" },
    body: "",
  };
};
