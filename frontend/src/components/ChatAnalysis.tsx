import { useState, useRef, useEffect } from 'react';
import { ChatMessage, AnalysisRequestBody, AnalysisResponse } from '../types/chat';
import { analyzeProperty } from '../utils/api';
import { useTabs } from '../context/TabsContext';
import { textStyles } from '../styles/textStyles';

const AGENT_NAME = 'negative_nancy';

const createAnalysisRequest = (
  propertyData: any,
  distanceInfo: any,
  chatHistory: ChatMessage[],
  currentQuestion?: string
): AnalysisRequestBody => ({
  property_data: propertyData,
  distance_info: distanceInfo,
  agent: AGENT_NAME,
  chat_history: chatHistory,
  current_question: currentQuestion,
});

const formatAnalysisData = (analysis: any): string => {
  if (!analysis) return '';
  
  let formatted = '';
  
  // Overview
  if (analysis.overview) {
    formatted += 'Overview:\n';
    formatted += `Property Type: ${analysis.overview.property_type}\n`;
    formatted += 'Key Features:\n' + analysis.overview.key_features.map((f: string) => `• ${f}`).join('\n') + '\n';
    formatted += `Condition: ${analysis.overview.condition}\n`;
    formatted += 'Unique Selling Points:\n' + analysis.overview.unique_selling_points.map((p: string) => `• ${p}`).join('\n') + '\n\n';
  }
  
  // Strengths
  if (analysis.strengths) {
    formatted += 'Strengths:\n';
    formatted += 'Physical Attributes:\n' + analysis.strengths.physical_attributes.map((s: string) => `• ${s}`).join('\n') + '\n';
    formatted += 'Location Advantages:\n' + analysis.strengths.location_advantages.map((s: string) => `• ${s}`).join('\n') + '\n';
    formatted += 'Investment Potential:\n' + analysis.strengths.investment_potential.map((s: string) => `• ${s}`).join('\n') + '\n';
    formatted += 'Lifestyle Benefits:\n' + analysis.strengths.lifestyle_benefits.map((s: string) => `• ${s}`).join('\n') + '\n\n';
  }
  
  // Concerns
  if (analysis.concerns) {
    formatted += 'Concerns:\n';
    formatted += 'Physical Issues:\n' + analysis.concerns.physical_issues.map((c: string) => `• ${c}`).join('\n') + '\n';
    formatted += 'Location Disadvantages:\n' + analysis.concerns.location_disadvantages.map((c: string) => `• ${c}`).join('\n') + '\n';
    formatted += 'Investment Risks:\n' + analysis.concerns.investment_risks.map((c: string) => `• ${c}`).join('\n') + '\n';
    formatted += 'Lifestyle Limitations:\n' + analysis.concerns.lifestyle_limitations.map((c: string) => `• ${c}`).join('\n') + '\n\n';
  }
  
  // Investment Analysis
  if (analysis.investment_analysis) {
    formatted += 'Investment Analysis:\n';
    formatted += `Price Assessment: ${analysis.investment_analysis.price_assessment}\n`;
    formatted += `Market Position: ${analysis.investment_analysis.market_position}\n`;
    formatted += `Growth Potential: ${analysis.investment_analysis.growth_potential}\n`;
    formatted += `Rental Potential: ${analysis.investment_analysis.rental_potential}\n`;
    formatted += 'Holding Costs:\n' + analysis.investment_analysis.holding_costs.map((c: string) => `• ${c}`).join('\n') + '\n\n';
  }
  
  // Recommendation
  if (analysis.recommendation) {
    formatted += 'Recommendation:\n';
    formatted += `Summary: ${analysis.recommendation.summary}\n`;
    formatted += 'Suitable Buyer Types:\n' + analysis.recommendation.suitable_buyer_types.map((t: string) => `• ${t}`).join('\n') + '\n';
    formatted += 'Key Considerations:\n' + analysis.recommendation.key_considerations.map((c: string) => `• ${c}`).join('\n') + '\n';
    formatted += 'Next Steps:\n' + analysis.recommendation.next_steps.map((s: string) => `• ${s}`).join('\n') + '\n\n';
  }
  
  return formatted;
};

export default function ChatAnalysis() {
  const { propertyData, distanceInfo, messages, setMessages, isSending, setIsSending } = useTabs();
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const startAnalysis = async () => {
    if (!propertyData) return;

    setIsSending(true);
    try {
      const requestBody = createAnalysisRequest(propertyData, distanceInfo, []);
      const response = await analyzeProperty(requestBody);

      if (response.analysis) {
        const formattedAnalysis = formatAnalysisData(response.analysis);
        setMessages([
          {
            content: formattedAnalysis || "I've completed my analysis of the property. What would you like to know more about?",
            timestamp: response.timestamp,
            agent: response.agent,
            analysis: response.analysis,
          },
        ]);
      }
    } catch (error) {
      console.error('Error starting analysis:', error);
      setMessages([
        {
          content: 'Sorry, there was an error starting the analysis. Please try again.',
          timestamp: new Date().toISOString(),
          agent: 'system',
        },
      ]);
    } finally {
      setIsSending(false);
    }
  };

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !propertyData) return;

    const userMessage: ChatMessage = {
      content: input,
      timestamp: new Date().toISOString(),
      agent: 'user',
    };

    setMessages([...messages, userMessage]);
    setInput('');
    setIsSending(true);

    try {
      const requestBody = createAnalysisRequest(propertyData, distanceInfo, messages, input);
      const response = await analyzeProperty(requestBody);

      if (response.analysis) {
        const formattedAnalysis = formatAnalysisData(response.analysis);
        setMessages([
          ...messages,
          userMessage,
          {
            content: formattedAnalysis || response.analysis.response || "I've analyzed your question. What else would you like to know?",
            timestamp: response.timestamp,
            agent: response.agent,
            analysis: response.analysis,
          },
        ]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages([
        ...messages,
        userMessage,
        {
          content: 'Sorry, there was an error processing your message. Please try again.',
          timestamp: new Date().toISOString(),
          agent: 'system',
        },
      ]);
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(e as any);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="mb-6">
          <button
            onClick={startAnalysis}
            disabled={isSending}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:bg-blue-300"
          >
            {isSending ? 'Analyzing...' : 'Start Analysis'}
          </button>
        </div>

        <div className="mb-6 h-[400px] overflow-y-auto border rounded-lg p-4 bg-gray-50">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`mb-4 ${
                message.agent === 'user' ? 'text-right' : 'text-left'
              }`}
            >
              <div
                className={`inline-block p-3 rounded-lg ${
                  message.agent === 'user'
                    ? 'bg-blue-100 text-blue-900'
                    : 'bg-gray-100 text-gray-900'
                }`}
              >
                <p className={textStyles.body.regular} style={{ whiteSpace: 'pre-line' }}>{message.content}</p>
                {message.agent !== 'user' && (
                  <p className="text-xs text-gray-500 mt-1">
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </p>
                )}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={sendMessage} className="flex space-x-4">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message..."
            className={`flex-1 p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${textStyles.body.regular}`}
            disabled={isSending}
            rows={3}
          />
          <button
            type="submit"
            disabled={isSending || !input.trim()}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:bg-blue-300"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
} 