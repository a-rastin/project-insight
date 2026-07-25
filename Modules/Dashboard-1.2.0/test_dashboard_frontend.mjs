import assert from "node:assert/strict";
function workspaceModel(role) {
  const psychiatrist = role === "PSYCHIATRIST";
  return {
    displayName: psychiatrist ? "Dr. Mina Rahimi" : "Ari Morgan",
    currentDateTime: "2026-07-06T17:30:00Z",
    workspace: {
      kind: role,
      title: "Workspace",
      buttons: psychiatrist
        ? [
            { id: "add-new-patient", title: "Add New Patient", status: "unavailable", reason: "contract endpoint returned HTTP 503", routeDiscovery: { method: "GET", href: "/internal/dashboard/module-routes/add-new-patient" } },
            { id: "patient-follow-up", title: "Patient Follow-up", status: "available", reason: "contract and readiness checks passed", routeDiscovery: { method: "GET", href: "/internal/dashboard/module-routes/patient-follow-up" } },
            { id: "list-of-patients", title: "List of Patients", status: "available", reason: "contract and readiness checks passed", routeDiscovery: { method: "GET", href: "/internal/dashboard/module-routes/list-of-patients" } },
            { id: "setting", title: "Setting", status: "available", reason: "contract and readiness checks passed", routeDiscovery: { method: "GET", href: "/internal/dashboard/module-routes/setting" } }
          ]
        : [
            {
              id: "user-management",
              title: "User Management",
              href: "/modules/user-management",
              status: "available",
              reason: "contract and readiness checks passed",
              routeDiscovery: { method: "GET", href: "/internal/dashboard/module-routes/user-management" }
            }
          ]
    },
    ...(psychiatrist ? { requiresDisclaimer: false, disclaimer: { acceptedAt: "2026-07-06T17:00:00Z" } } : {})
  };
}

function fakeElement() {
  return {
    disabled: false,
    addEventListener() {}
  };
}

async function renderScenario(role) {
  const app = {
    innerHTML: "",
    querySelector() {
      return fakeElement();
    },
    querySelectorAll() {
      return [];
    }
  };

  globalThis.document = {
    querySelector(selector) {
      assert.equal(selector, "#app");
      return app;
    }
  };
  globalThis.location = {
    search: `?session=${role.toLowerCase()}-session`,
    hostname: "127.0.0.1",
    assign() {}
  };
  globalThis.history = { replaceState() {} };
  globalThis.fetch = async (url) => {
    if (url === "/internal/dashboard/config") {
      return {
        ok: true,
        async json() {
          return { mockAuthEnabled: false };
        }
      };
    }
    if (url === "/internal/dashboard/session") {
      return {
        ok: true,
        async json() {
          return { sessionId: `${role.toLowerCase()}-session` };
        }
      };
    }
    assert.equal(String(url), "/internal/dashboard/workspace");
    return {
      ok: true,
      async json() {
        return workspaceModel(role);
      }
    };
  };

  const moduleUrl = new URL("./dashboard.js", import.meta.url);
  moduleUrl.search = `role=${role}&t=${Date.now()}`;
  await import(moduleUrl.href);

  const deadline = Date.now() + 1000;
  while (!app.innerHTML.includes("Module Launch") && Date.now() < deadline) {
    await new Promise((resolve) => setTimeout(resolve, 10));
  }
  return app.innerHTML;
}

const psychiatristHtml = await renderScenario("PSYCHIATRIST");
assert.match(psychiatristHtml, /<h1>Workspace<\/h1>/);
assert.match(psychiatristHtml, /Dr\. Mina Rahimi/);
assert.match(psychiatristHtml, /Jul|07\/06|6\/7|06\/07/);
for (const title of ["Add New Patient", "Patient Follow-up", "List of Patients", "Setting"]) {
  assert.match(psychiatristHtml, new RegExp(title));
}
assert.match(psychiatristHtml, /unavailable/i);
assert.match(psychiatristHtml, /contract endpoint returned HTTP 503/);
assert.match(psychiatristHtml, /data-module="add-new-patient" disabled/);

const adminHtml = await renderScenario("ADMIN");
assert.match(adminHtml, /<h1>Workspace<\/h1>/);
assert.match(adminHtml, /Ari Morgan/);
assert.doesNotMatch(adminHtml, /Dr\. Ari Morgan/);
assert.match(adminHtml, /User Management/);
assert.match(adminHtml, /data-module="user-management"/);
