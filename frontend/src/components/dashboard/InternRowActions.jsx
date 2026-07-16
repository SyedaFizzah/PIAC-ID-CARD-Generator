export default function InternRowActions({ intern, onGenerateCard, onDownloadCard, onDownloadDocument }) {
  return (
    <div className="flex flex-col items-start gap-2">
      {intern.card_front_path ? (
        <button
          onClick={() => onDownloadCard(intern.id, intern.unique_id)}
          className="text-pia-green underline"
        >
          Download Card
        </button>
      ) : (
        <button
          onClick={() => onGenerateCard(intern.id)}
          className="bg-pia-green text-white px-3 py-1 rounded-lg text-xs"
        >
          Generate Card
        </button>
      )}

      <button
        onClick={() => onDownloadDocument(intern.id, "security-letter")}
        className="bg-pia-green text-white px-3 py-1 rounded-lg text-xs"
      >
        Generate Security Letter
      </button>

      <button
        onClick={() => onDownloadDocument(intern.id, "offer-letter")}
        className="bg-pia-green text-white px-3 py-1 rounded-lg text-xs"
      >
        Generate Offer Letter
      </button>

      {/* Certificate template not ready yet -- re-enable once the design is
          approved. Backend route still works fine if you need to test it
          directly.
      <button
        onClick={() => onDownloadDocument(intern.id, "certificate")}
        className="bg-pia-green text-white px-3 py-1 rounded-lg text-xs"
      >
        Generate Certificate
      </button>
      */}
    </div>
  );
}
