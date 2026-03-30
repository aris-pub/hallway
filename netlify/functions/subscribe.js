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
    return { statusCode: 302, headers: { Location: "/subscribe-error/" }, body: "" };
  }

  try {
    await resendRequest("/emails", {
      from: "The Hallway Track <hallway@updates.aris.pub>",
      to: [email],
      reply_to: "hello@aris.pub",
      subject: "Subscribed to The Hallway Track",
      html: `<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #0a0a0a; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="text-align: center; margin-bottom: 30px;">
        <h1 style="color: #157067; margin: 0; font-weight: 400;">The Hallway Track</h1>
    </div>

    <div style="background: #f5f7f6; border-radius: 12px; padding: 30px; margin-bottom: 30px; border-left: 4px solid #157067;">
        <p style="font-size: 16px; margin: 0 0 20px 0;">You're subscribed to The Hallway Track, a weekly curated link roundup on how AI is affecting the practice of science.</p>
        <p style="font-size: 16px; margin: 0;">Each edition will arrive in your inbox on Mondays.</p>
    </div>

    <div style="text-align: center; color: #7a7a7a; font-size: 14px; border-top: 1px solid #e8e8e4; padding-top: 20px;">
        <p style="margin: 0; font-size: 12px;">
            Part of <a href="https://aris.pub" style="color: #157067;">The Aris Program</a>
        </p>
    </div>
</body>
</html>`,
    });
  } catch (err) {
    console.error("Failed to send confirmation:", err.message);
  }

  try {
    await resendRequest("/emails", {
      from: "The Hallway Track <hallway@updates.aris.pub>",
      to: ["hello@aris.pub"],
      subject: `New subscriber: ${email}`,
      text: `${email} just subscribed to The Hallway Track.`,
    });
  } catch (err) {
    console.error("Failed to send admin notification:", err.message);
  }

  return {
    statusCode: 302,
    headers: { Location: "/subscribed/" },
    body: "",
  };
};
