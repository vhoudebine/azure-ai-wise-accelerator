interface EvaluationPanelProps {
    evaluation: {
        classification: string | null;
        overall_score: 0;
        criteria: Array<any>;
        rationale: string;
        improvement_suggestion: string;
        factCheckTotalChecked: number;
        factCheckTotalCorrect: number;
        factCheckTotalIncorrect: number;
        factCheckTotalUnknown: number;
        factDetails: Array<any>;
    };
}

export default function EvaluationPanel({ evaluation }: EvaluationPanelProps) {
    if (!evaluation.classification) {
        return;
    }

    return (
        <div>
            <div className="space-y-4">
                <div className="flex flex-col gap-4">
                    <div className="flex flex-row justify-between">
                        <h2>Overall Interaction:</h2>
                        <strong>
                            <span>{evaluation.classification}</span>
                        </strong>
                    </div>
                    <div className="flex flex-row justify-between">
                        <h2>Score:</h2>
                        <strong>
                            <span>{evaluation.overall_score}</span>
                        </strong>
                    </div>
                    <div className="flex flex-row justify-between">
                        <h2>Accurately Stated Facts:</h2>
                        <strong>
                            <span>{evaluation.factCheckTotalCorrect}</span>
                        </strong>
                    </div>

                    <div className="flex flex-row justify-between">
                        <h2>Inaccurately Stated Facts:</h2>
                        <strong>
                            <span>{evaluation.factCheckTotalIncorrect}</span>
                        </strong>
                    </div>

                    <div className="flex flex-row justify-between">
                        <h2>Unverified Stated Facts:</h2>
                        <strong>
                            <span>{evaluation.factCheckTotalUnknown}</span>
                        </strong>
                    </div>

                    <div className="flex flex-row justify-between">
                        <h2>Total Checked Facts:</h2>
                        <strong>
                            <span>{evaluation.factCheckTotalChecked}</span>
                        </strong>
                    </div>
                    <hr />
                    <div className="flex flex-col">
                        <h2 className="mb-4 text-center">- Rationale -</h2>
                        <span>{evaluation.rationale}</span>
                    </div>

                    <div className="flex flex-col">
                        <h2 className="mb-4 text-center">- Suggestions -</h2>
                        <span>{evaluation.improvement_suggestion}</span>
                    </div>
                    <hr />
                    <div className="flex flex-col">
                        <h2 className="mb-4 text-center">- Fact Checking -</h2>
                        {evaluation.factDetails.map((fact, index) => (
                            <div key={index} className={`${index % 2 === 0 ? "bg-gray-200" : "bg-gray-100"} mb-4 flex flex-col gap-2`}>
                                <div className="flex flex-row justify-between">
                                    <span>{fact.fact}</span>
                                    {fact.accuracy === "accurate" && <span>✔️</span>}
                                    {fact.accuracy === "inaccurate" && <span>❌</span>}
                                    {fact.accuracy === "unknown" && <span>❓</span>}
                                </div>
                                {!fact.is_correct && (
                                    <div className="flex flex-col italic">
                                        <span>{fact.citation}</span>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
                <div />
            </div>
        </div>
    );
}
