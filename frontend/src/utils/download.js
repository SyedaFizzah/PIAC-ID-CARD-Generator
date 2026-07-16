import client from "../api/client";

// Turns an axios blob response into a real file download, honoring the
// filename the backend suggests via Content-Disposition when present.
export function downloadBlobPdf(response, defaultName) {
  const url = window.URL.createObjectURL(
    new Blob([response.data], { type: "application/pdf" })
  );

  const disposition = response.headers["content-disposition"];
  let filename = defaultName;

  if (disposition) {
    const match = disposition.match(/filename="(.+)"/);
    if (match) {
      filename = match[1];
    }
  }

  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  window.URL.revokeObjectURL(url);
}

export function downloadCardPdf(id, uniqueId) {
  return client
    .get(`/interns/${id}/card/pdf`, { responseType: "blob" })
    .then((res) => downloadBlobPdf(res, `${uniqueId}.pdf`));
}

export function downloadDocument(id, documentType) {
  return client
    .get(`/interns/${id}/${documentType}/pdf`, { responseType: "blob" })
    .then((res) => downloadBlobPdf(res, `${id}_${documentType}.pdf`));
}
