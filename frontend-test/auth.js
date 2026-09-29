window.SentraAuth = (() => {
  const COGNITO_REGION = "us-east-1";
  const COGNITO_CLIENT_ID = "17cubucr8ln5m4gralm4hh0r95";
  const COGNITO_ENDPOINT = `https://cognito-idp.${COGNITO_REGION}.amazonaws.com/`;
  const API_URL = "https://29z5qm8jke.execute-api.us-east-1.amazonaws.com/test";

  function storeTokens(authResult) {
    const accessToken = authResult && authResult.AccessToken;

    if (!accessToken) {
      throw new Error("Cognito did not return an access token");
    }

    localStorage.setItem("access_token", accessToken);
    localStorage.setItem("id_token", authResult.IdToken);

    if (authResult.RefreshToken) {
      localStorage.setItem("refresh_token", authResult.RefreshToken);
    }
  }

  async function callApi() {
    const accessToken = localStorage.getItem("access_token");
    const response = await fetch(API_URL, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });

    let data;
    const responseText = await response.text();
    try {
      data = JSON.parse(responseText);
    } catch {
      data = responseText;
    }

    return { response, data };
  }

  return {
    COGNITO_CLIENT_ID,
    COGNITO_ENDPOINT,
    storeTokens,
    callApi,
  };
})();
