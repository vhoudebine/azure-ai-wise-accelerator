import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";

export default function PersonaPanel() {
    const [fetchedPersonas, setFetchedPersonas] = useState<{
        personas: {
            age: number;
            customer_profile: string;
            difficulty: string;
            family: string;
            gender: string;
            id: string;
            name: string;
            occupation: string;
            personality: string;
            voice: string;
        }[];
    }>({
        personas: []
    });
    useEffect(() => {
        const fetchedConfig = async () => {
            const response = await fetch("/config/get-personas");
            const data = await response.json();
            console.log(data);
            setFetchedPersonas(data);
        };
        fetchedConfig();
    }, []);

    return (
        <div className="space-y-8">
            {fetchedPersonas.personas.map(persona => {
                return (
                    <Card key={persona.id} className="relative border-gray-300 p-2 hover:cursor-pointer hover:border-purple-400 hover:shadow-lg">
                        <span className="absolute right-0 top-0 rounded-tr-sm bg-purple-400 pl-1 pr-1 text-sm italic text-white">{persona.difficulty}</span>
                        <span className="block text-center font-medium">{persona.name}</span>
                        <ul>
                            <li>{`${persona.age} ${persona.gender}`}</li>
                            <li>{persona.family}</li>
                            <li>{persona.occupation}</li>
                            <li>{persona.personality}</li>
                            <li>{persona.customer_profile}</li>
                        </ul>
                    </Card>
                );
            })}
        </div>
    );
}
