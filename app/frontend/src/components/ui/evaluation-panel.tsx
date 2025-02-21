interface EvaluationPanelProps {
    evaluation: {
        classification: string | null;
        overall_score: 0;
        criteria: Array<any>;
        rationale: string;
        improvement_suggestion: string;
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
                    <hr />
                    <div className="flex flex-col">
                        <h2 className="text-center">- Rationale -</h2>
                        <span>{evaluation.rationale}</span>
                    </div>

                    <div className="flex flex-col">
                        <h2 className="text-center">- Suggestions -</h2>
                        <span>{evaluation.improvement_suggestion}</span>
                    </div>
                </div>
                <div />
            </div>
        </div>
    );
}
