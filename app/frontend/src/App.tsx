import { useState, useEffect } from "react";
import { Mic, MicOff, Menu, MessageSquare, SendHorizonal, Loader } from "lucide-react";
import { useTranslation } from "react-i18next";

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet";

import StatusMessage from "@/components/ui/status-message";
// import MenuPanel from "@/components/ui/menu-panel";
import PersonaPanel from "@/components/ui/persona-panel";
import TranscriptPanel from "@/components/ui/transcript-panel";
import EvaluationPanel from "./components/ui/evaluation-panel";
import Settings from "@/components/ui/settings";
import useRealTime from "@/hooks/useRealtime";
import useAudioRecorder from "@/hooks/useAudioRecorder";
import useAudioPlayer from "@/hooks/useAudioPlayer";
import { ThemeProvider, useTheme } from "./context/theme-context";
import { AzureSpeechProvider } from "@/context/azure-speech-context";

function App() {
    const [isRecording, setIsRecording] = useState(false);
    const [isMobile, setIsMobile] = useState(false);
    const { theme } = useTheme();

    const [transcripts, setTranscripts] = useState<Array<{ text: string; isUser: boolean; timestamp: Date }>>(() => {
        return [];
    });

    const [evaluation, setEvaluation] = useState<{
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
    }>({
        classification: null,
        overall_score: 0,
        criteria: [],
        rationale: "",
        improvement_suggestion: "",
        factCheckTotalChecked: 0,
        factCheckTotalCorrect: 0,
        factCheckTotalIncorrect: 0,
        factCheckTotalUnknown: 0,
        factDetails: []
    });

    const [isLoading, setIsLoading] = useState<boolean>(false);

    const realtime = useRealTime({
        enableInputAudioTranscription: true,
        onWebSocketOpen: () => console.log("WebSocket connection opened"),
        onWebSocketClose: () => console.log("WebSocket connection closed"),
        onWebSocketError: event => console.error("WebSocket error:", event),
        onReceivedError: message => console.error("error", message),
        onReceivedResponseAudioDelta: message => {
            isRecording && playAudio(message.delta);
        },
        onReceivedInputAudioBufferSpeechStarted: () => {
            stopAudioPlayer();
        },
        onReceivedInputAudioTranscriptionCompleted: message => {
            const newTranscriptItem = {
                text: message.transcript,
                isUser: true,
                timestamp: new Date()
            };
            setTranscripts(prev => [...prev, newTranscriptItem]);
        },
        onReceivedResponseDone: message => {
            const transcript = message.response.output.map(output => output.content?.map(content => content.transcript).join(" ")).join(" ");
            if (!transcript) return;

            const newTranscriptItem = {
                text: transcript,
                isUser: false,
                timestamp: new Date()
            };
            setTranscripts(prev => [...prev, newTranscriptItem]);
        }
    });

    const { reset: resetAudioPlayer, play: playAudio, stop: stopAudioPlayer } = useAudioPlayer();
    const { start: startAudioRecording, stop: stopAudioRecording } = useAudioRecorder({
        onAudioRecorded: realtime.addUserAudio
    });

    const onToggleListening = async () => {
        if (!isRecording) {
            realtime.startSession();
            await startAudioRecording();
            resetAudioPlayer();
            setIsRecording(true);
        } else {
            await stopAudioRecording();
            stopAudioPlayer();
            realtime.inputAudioBufferClear();
            setIsRecording(false);
        }
    };

    const handleEvaluate = async () => {
        setIsLoading(true);
        const adaptedTranscript = transcripts.map(message => ({
            speaker: message.isUser ? "Advisor" : "Client",
            text: message.text.trim() // Remove any leading or trailing whitespace
        }));
        const payload = { transcript: adaptedTranscript };
        const result = await fetch("/evaluation/transcript-evaluate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });
        const evalReceived = await result.json();
        console.log(evalReceived);
        setEvaluation(previous => ({
            ...previous,
            classification: evalReceived.rule_based_eval.evaluation.classification,
            overall_score: evalReceived.rule_based_eval.evaluation.overall_score,
            criteria: [...evalReceived.rule_based_eval.evaluation.criteria],
            rationale: evalReceived.rule_based_eval.evaluation.rationale,
            improvement_suggestion: evalReceived.rule_based_eval.evaluation.improvement_suggestion,
            factCheckTotalChecked: evalReceived.fact_check_eval.total_facts_shared,
            factCheckTotalCorrect: evalReceived.fact_check_eval.accurate_facts_count,
            factCheckTotalIncorrect: evalReceived.fact_check_eval.inaccurate_facts_count,
            factCheckTotalUnknown: evalReceived.fact_check_eval.unverifiable_facts_count,
            factDetails: [...evalReceived.fact_check_eval.fact_details]
        }));
        setIsLoading(false);
    };

    const { t } = useTranslation();

    useEffect(() => {
        const checkMobile = () => {
            setIsMobile(window.innerWidth < 768);
        };
        checkMobile();
        window.addEventListener("resize", checkMobile);
        return () => window.removeEventListener("resize", checkMobile);
    }, []);

    return (
        <div className={`min-h-screen bg-background p-4 text-foreground ${theme}`}>
            <div className="mx-auto max-w-7xl">
                <div className="relative mb-6 flex flex-col items-center md:mb-4">
                    <h1 className="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-center text-4xl font-bold text-transparent md:text-6xl">
                        WISE
                    </h1>
                    <h2 className="margin-l purple m-4 text-2xl font-bold">
                        AI simulation based solution for enablement in the Financial Services Industry on Azure
                    </h2>
                    <div className="absolute right-0 top-1/2 -translate-y-1/2 transform">
                        <Settings isMobile={isMobile} />
                    </div>
                </div>

                <div className="grid grid-cols-1 gap-4 md:grid-cols-4 md:gap-8">
                    {/* Mobile Menu Button */}
                    <Sheet>
                        <SheetTrigger asChild>
                            <Button variant="outline" className="mb-4 flex w-full items-center justify-center md:hidden">
                                <Menu className="mr-2 h-4 w-4" />
                                View Persona
                            </Button>
                        </SheetTrigger>
                        <SheetContent side="left" className="w-[300px] sm:w-[400px]">
                            <SheetHeader>
                                <SheetTitle>Current Persona</SheetTitle>
                            </SheetHeader>
                            <div className="h-[calc(100vh-4rem)] overflow-auto pr-4">
                                <PersonaPanel />
                            </div>
                        </SheetContent>
                    </Sheet>

                    {/* Desktop Menu Panel */}
                    <Card className="hidden p-6 md:block">
                        <h2 className="mb-4 text-center font-semibold">Current Persona</h2>
                        <div className="h-[calc(100vh-24rem)] overflow-auto pr-4">
                            <PersonaPanel />
                        </div>
                    </Card>

                    {/* Center Panel - Recording Button and Order Summary */}
                    <Card className="p-6 md:overflow-auto">
                        <h2 className="mb-4 text-center font-semibold">Controls</h2>
                        <div className="space-y-8">
                            <div className="mb-4 flex flex-col items-center justify-center gap-16">
                                <div>
                                    <Button
                                        onClick={onToggleListening}
                                        className={`h-12 w-60 ${isRecording ? "bg-red-600 hover:bg-red-700" : "bg-purple-500 hover:bg-purple-600"}`}
                                        aria-label={isRecording ? t("app.stopRecording") : t("app.startRecording")}
                                    >
                                        {isRecording ? (
                                            <>
                                                <MicOff className="mr-2 h-4 w-4" />
                                                {t("app.stopConversation")}
                                            </>
                                        ) : (
                                            <>
                                                <Mic className="mr-2 h-6 w-6" />
                                            </>
                                        )}
                                    </Button>
                                    <StatusMessage isRecording={isRecording} />
                                </div>
                                {!isRecording && !isLoading && transcripts.length > 0 && (
                                    <div className="mb-4 flex flex-col items-center justify-center gap-4">
                                        <Button
                                            onClick={handleEvaluate}
                                            className={`h-12 w-60 ${isRecording ? "bg-red-600 hover:bg-red-700" : "bg-purple-500 hover:bg-purple-600"}`}
                                            aria-label={isRecording ? t("app.stopRecording") : t("app.startRecording")}
                                        >
                                            <SendHorizonal className="mr-2 h-6 w-6" />
                                        </Button>
                                        <span>Send for Evaluation</span>
                                    </div>
                                )}
                                {isLoading && (
                                    <div className="mb-4 flex flex-col items-center justify-center gap-4">
                                        <Button
                                            onClick={handleEvaluate}
                                            className={`h-12 w-60 ${isRecording ? "bg-red-600 hover:bg-red-700" : "bg-purple-500 hover:bg-purple-600"}`}
                                            aria-label={isRecording ? t("app.stopRecording") : t("app.startRecording")}
                                        >
                                            <Loader className="animate-spin" />
                                        </Button>
                                        <span>Sending for Evaluation..</span>
                                    </div>
                                )}
                            </div>
                        </div>
                    </Card>

                    {/* Mobile Transcript Button */}
                    <Sheet>
                        <SheetTrigger asChild>
                            <Button variant="outline" className="mt-4 flex w-full items-center justify-center md:hidden">
                                <MessageSquare className="mr-2 h-4 w-4" />
                                View Transcript
                            </Button>
                        </SheetTrigger>
                        <SheetContent side="right" className="w-[300px] sm:w-[400px]">
                            <SheetHeader>
                                <SheetTitle>Transcript History</SheetTitle>
                            </SheetHeader>
                            <div className="h-[calc(100vh-4rem)] overflow-auto pr-4">
                                <TranscriptPanel transcripts={transcripts} />
                            </div>
                        </SheetContent>
                    </Sheet>

                    {/* Desktop Transcript Panel */}
                    <Card className="hidden p-6 md:block">
                        <h2 className="mb-4 text-center font-semibold">Transcript History</h2>
                        <div className="h-[calc(100vh-24rem)] overflow-auto pr-4">
                            <TranscriptPanel transcripts={transcripts} />
                        </div>
                    </Card>

                    <Card className="hidden p-6 md:block">
                        <h2 className="mb-4 text-center font-semibold">Evaluation</h2>
                        <div className="h-[calc(100vh-24rem)] overflow-auto pr-4">
                            <EvaluationPanel evaluation={evaluation} />
                        </div>
                    </Card>
                </div>
            </div>
            {/* <Button onClick={() => onUserRequestShowImage("Espresso")}>Show Espresso Image</Button>
            {imageDialogOpen && <ImageDialog imageUrl={imageUrl} onClose={() => setImageDialogOpen(false)} />} */}
        </div>
    );
}

export default function RootApp() {
    return (
        <ThemeProvider>
            {/* <DummyDataProvider> */}
            <AzureSpeechProvider>
                <App />
            </AzureSpeechProvider>
            {/* </DummyDataProvider> */}
        </ThemeProvider>
    );
}
