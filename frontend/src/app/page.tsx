import { TabsProvider } from '../context/TabsContext';
import Home from '../components/Home';

export default function Page() {
  return (
    <TabsProvider>
      <Home />
    </TabsProvider>
  );
}
