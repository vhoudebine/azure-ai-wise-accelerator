import { Card } from "@/components/ui/card";

export default function PersonaPanel() {
    return (
        <div className="space-y-8">
            <Card className="relative border-purple-400 p-2 hover:cursor-pointer hover:border-purple-400 hover:shadow-lg">
                <span className="absolute right-0 top-0 rounded-tr-sm bg-purple-400 pl-1 pr-1 text-sm italic text-white">Hard</span>
                <span className="block text-center font-medium">John</span>
                <ul>
                    <li>42y old male</li>
                    <li>Medical doctor</li>
                    <li>Married, 3 Kids</li>
                    <li>Skeptical</li>
                    <li>Invests in Real Estate</li>
                </ul>
            </Card>
            <Card className="relative border-gray-300 p-2 hover:cursor-pointer hover:border-purple-400 hover:shadow-lg">
                <span className="absolute right-0 top-0 rounded-tr-sm bg-purple-400 pl-1 pr-1 text-sm italic text-white">Medium</span>
                <span className="block text-center font-medium">Amy</span>
                <ul>
                    <li>39y old female</li>
                    <li>Tech exec</li>
                    <li>No dependent</li>
                    <li>Enthusiastic</li>
                    <li>Crypto investor</li>
                </ul>
            </Card>
        </div>
    );
}
