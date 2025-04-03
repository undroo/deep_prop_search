import { useState, useRef, useEffect } from 'react';
import { AnalysisData, PropertyData} from '../types/property';

interface ChatMessage {
  content: string;
  timestamp: string;
  agent?: string;
  analysis?: any;
}



interface ChatAnalysisProps {
  property: PropertyData;
  distanceInfo?: any;
}

export default function ChatAnalysis({ property, distanceInfo }: ChatAnalysisProps) {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<AnalysisData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isSending, setIsSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const startAnalysis = async () => {
    setIsAnalyzing(true);
    setError(null);
    try {
      console.log('Starting analysis with property data:', {
        propertyKeys: Object.keys(property),
        hasDistanceInfo: !!distanceInfo,
        distanceInfoKeys: distanceInfo ? Object.keys(distanceInfo) : []
      });

      const requestBody = {
        property_data: property,
        distance_info: distanceInfo,
        agent: 'negative_nancy'
      };
      console.log('Sending request to:', 'http://localhost:8000/api/v1/analyze');
      console.log('Request body:', JSON.stringify(requestBody, null, 2));

      const response = await fetch('http://localhost:8000/api/v1/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      console.log('Response status:', response.status);
      console.log('Response headers:', Object.fromEntries(response.headers.entries()));

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Error response:', errorText);
        throw new Error(`Failed to get analysis: ${response.status} ${errorText}`);
      }

      const data = await response.json();
      console.log('Response data:', data);
      console.log('Response data type:', typeof data);
      console.log('Response data keys:', Object.keys(data));
      console.log('Analysis field exists:', 'analysis' in data);
      console.log('Analysis field type:', typeof data.analysis);
      console.log('Analysis field value:', data.analysis);
      
      if (!data.analysis || Object.keys(data.analysis).length === 0) {
        console.warn('No analysis data in response:', data);
      }
      
      setAnalysis(data.analysis);
      
      // Add the initial analysis to messages
      setMessages([{
        content: "I've completed my analysis of the property. What would you like to know more about?",
        timestamp: new Date().toISOString(),
        agent: 'Negative Nancy',
        analysis: data.analysis
      }]);
    } catch (err) {
      console.error('Analysis error:', err);
      setError('Failed to get property analysis. Please try again.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isSending) return;

    setIsSending(true);
    setError(null);

    // Add user message to chat
    const userMessage: ChatMessage = {
      content: inputMessage,
      timestamp: new Date().toISOString(),
    };
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');

    try {
      const requestBody = {
        property_data: property,
        distance_info: distanceInfo,
        agent: 'negative_nancy',
        chat_history: messages,
        current_question: inputMessage
      };

      const response = await fetch('http://localhost:8000/api/v1/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error(`Failed to send message: ${response.status}`);
      }

      const data = await response.json();
      
      // Add agent's response to chat
      setMessages(prev => [...prev, {
        content: data.analysis.response,
        timestamp: data.timestamp,
        agent: data.agent
      }]);
    } catch (err) {
      console.error('Error sending message:', err);
      setError('Failed to send message. Please try again.');
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const renderListSection = (title: string, items: string[]) => {
    if (!items || items.length === 0) return null;
    
    return (
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
        <ul className="list-disc pl-5 space-y-1">
          {items.map((item, index) => (
            <li key={index} className="text-gray-700">{item}</li>
          ))}
        </ul>
      </div>
    );
  };

  const renderTextSection = (title: string, content: string) => {
    if (!content) return null;
    
    return (
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
        <p className="text-gray-700">{content}</p>
      </div>
    );
  };

  const renderSection = (title: string, content: any) => {
    if (!content) return null;
    
    return (
      <div className="mb-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">{title}</h2>
        {Object.entries(content).map(([key, value]) => {
          const formattedKey = key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
          if (Array.isArray(value)) {
            return <div key={key}>{renderListSection(formattedKey, value)}</div>;
          } else if (typeof value === 'string') {
            return <div key={key}>{renderTextSection(formattedKey, value)}</div>;
          }
          return null;
        })}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {!analysis ? (
        <div className="text-center">
          <button
            onClick={startAnalysis}
            disabled={isAnalyzing}
            className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-lg shadow-sm text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
          >
            {isAnalyzing ? (
              <>
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Analyzing...
              </>
            ) : (
              'Start Chat with Negative Nancy'
            )}
          </button>
        </div>
      ) : (
        <div className="flex flex-col h-[600px]">
          {/* Chat Messages */}
          <div className="flex-1 overflow-y-auto space-y-4 mb-4 p-4 bg-white rounded-lg shadow">
            {messages.map((message, index) => (
              <div key={index} className={`flex ${message.agent ? 'items-start' : 'items-end justify-end'}`}>
                {message.agent && (
                  <div className="flex-shrink-0 mr-3">
                    <div className="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center">
                      <span className="text-purple-600 font-medium">N</span>
                    </div>
                  </div>
                )}
                <div className={`flex-1 ${message.agent ? 'bg-purple-50' : 'bg-blue-50'} rounded-lg p-4 max-w-[80%]`}>
                  <p className="text-gray-800">{message.content}</p>
                  {message.analysis && (
                    <div className="mt-4">
                      {renderSection('Overview', message.analysis.overview)}
                      {renderSection('Strengths', message.analysis.strengths)}
                      {renderSection('Concerns', message.analysis.concerns)}
                      {renderSection('Investment Analysis', message.analysis.investment_analysis)}
                      {renderSection('Recommendation', message.analysis.recommendation)}
                      {renderSection('Property Analysis', message.analysis.property_analysis)}
                      {renderSection('Location Assessment', message.analysis.location_assessment)}
                      {renderSection('Market Analysis', message.analysis.market_analysis)}
                      {renderSection('Buyer Recommendations', message.analysis.buyer_recommendations)}
                      {renderSection('Inspection Checklist', message.analysis.inspection_checklist)}
                      {renderSection('Risk Assessment', message.analysis.risk_assessment)}
                    </div>
                  )}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          {/* Message Input */}
          <div className="flex space-x-4">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask a question about the property..."
              className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none bg-white text-gray-900 placeholder-gray-500"
              rows={2}
              disabled={isSending}
            />
            <button
              onClick={sendMessage}
              disabled={isSending || !inputMessage.trim()}
              className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
            >
              {isSending ? (
                <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              ) : (
                'Send'
              )}
            </button>
          </div>
        </div>
      )}

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-600">{error}</p>
        </div>
      )}
    </div>
  );
} 